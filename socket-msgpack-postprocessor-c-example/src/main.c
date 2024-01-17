// Standard system includes
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

// Local includes
#include "mpack.h"
#include "sclbl_socket_utils.h"

#define STRLEN( s ) ( sizeof( s ) / sizeof( s[0] ) )

// Flag to keep track of interrupts
volatile sig_atomic_t interrupt_flag = false;

char *processMpackDocument( const char *input_buffer, size_t input_buffer_length, size_t *output_buffer_length );
/**
 * @brief Function to handle interrupt signals
 *
 * When the Scailable Runtime is stopped, it sends an interrupt signal to all postprocessors it started
 * and waits for them to exit.
 *
 * This function sets a global interrupt flag which stops the socket listener loop. After the loop is broken
 * the socket is closed and the application exits gracefully.
 *
 * @param sig
 */
void handle_interrupt( int sig );

// Main function, the entry point of the application
int main( int argc, char *argv[] ) {
    // Check for the correct number of command line arguments
    if ( argc != 2 ) {
        printf( "EXAMPLE POSTPROCESSOR: Started with incorrect command line arguments.\n" );
        exit( 2 );
    }

    // Set signal handler to listen for interrupt signals
    signal( SIGINT, handle_interrupt );

    const char *socket_path = argv[1];

    printf( "EXAMPLE POSTPROCESSOR: Starting up with socket path: %s.\n", socket_path );

    char *input_buffer = NULL;
    size_t allocated_buffer_size = 0;
    uint32_t message_length;

    // Create a listener socket
    int socket_fd = sclbl_socket_create_listener( socket_path );

    // Main loop: continues until an interrupt signal is received
    while ( interrupt_flag == false ) {
        // Wait for a message on the socket
        int connection_fd = sclbl_socket_await_message( socket_fd, &allocated_buffer_size, &input_buffer, &message_length );

        // If connection times out, it continues to wait for the message again
        if ( connection_fd == -1 ) {
            continue;
        }

        // Process the Mpack document
        size_t output_length;
        char *output_message = processMpackDocument( input_buffer, message_length, &output_length );

        // Send the processed output back to the socket
        sclbl_socket_send_to_connection( connection_fd, output_message, output_length );

        // Close the connection
        if ( close( connection_fd ) == -1 ) {
            fprintf( stderr, "EXAMPLE POSTPROCESSOR: Warning: Sender socket close error!\n" );
        }
    }

    printf( "EXAMPLE POSTPROCESSOR: Exiting.\n" );
}

/**
 * @brief This function is an example of how you can parse, alter and return a MessagePack message.
 * The incoming message always follows a specific schema, and it is important to maintain this schema if you wish
 * to make changes. If the returned message does not follow the schema, this could cause problems and even crashes
 * in the Scailable runtime.
 * 
 * Schema:
 * 
 * 1. "Outputs" ({OutputName:bin})
 * 2. "OutputRanks" ([num tensors]i32)
 * 3. "OutputShapes" ([num tensors][rank]i64)
 * 4. "OutputDataTypes" ([num tensors]i32)
 * 
 * @param input_buffer 
 * @param input_buffer_length 
 * @param output_buffer_length 
 * @return char* 
 */
char *processMpackDocument( const char *input_buffer, size_t input_buffer_length, size_t *output_buffer_length ) {

    ////////////////////////////////////////////////////
    //// Parse input data
    ////////////////////////////////////////////////////

    // Initialize Node API tree
    mpack_tree_t tree;
    mpack_tree_init_data( &tree, input_buffer, input_buffer_length );
    mpack_tree_parse( &tree );
    mpack_node_t inference_results_root = mpack_tree_root( &tree );

    // Read outputs ([num tensors]bin)
    mpack_node_t outputs_map = mpack_node_map_cstr( inference_results_root, "Outputs" );
    size_t num_tensors = mpack_node_map_count( outputs_map );

    // Read output ranks ([num tensors]i32)
    mpack_node_t outputs_ranks_array = mpack_node_map_cstr( inference_results_root, "OutputRanks" );
    int32_t *output_ranks = malloc( sizeof( int32_t ) * num_tensors );
    for ( size_t index = 0; index < num_tensors; index++ ) {
        output_ranks[index] = mpack_node_i32( mpack_node_array_at( outputs_ranks_array, index ) );
    }

    // Read output shapes ([num tensors][rank]i64)
    mpack_node_t outputs_shapes_outer_array = mpack_node_map_cstr( inference_results_root, "OutputShapes" );
    int64_t **output_shapes = malloc( sizeof( int64_t * ) * num_tensors );
    for ( size_t output_index = 0; output_index < num_tensors; output_index++ ) {
        mpack_node_t outputs_shapes_inner_array = mpack_node_array_at( outputs_shapes_outer_array, output_index );
        output_shapes[output_index] = malloc( sizeof( int64_t ) * output_ranks[output_index] );
        for ( int32_t rank_index = 0; rank_index < output_ranks[output_index]; rank_index++ ) {
            output_shapes[output_index][rank_index] = mpack_node_i64( mpack_node_array_at( outputs_shapes_inner_array, rank_index ) );
        }
    }

    // Read output data types ([num tensors]i32)
    mpack_node_t output_data_types_array = mpack_node_map_cstr( inference_results_root, "OutputDataTypes" );
    int32_t *output_data_types = malloc( sizeof( int32_t ) * num_tensors );
    for ( uint32_t index = 0; index < num_tensors; index++ ) {
        output_data_types[index] = mpack_node_i32( mpack_node_array_at( output_data_types_array, index ) );
    }

    char **output_names = malloc( sizeof( char * ) * num_tensors );
    const char **output_datas = malloc( sizeof( char * ) * num_tensors );
    size_t *output_sizes = malloc( sizeof( size_t ) * num_tensors );
    for ( size_t tensor_index = 0; tensor_index < num_tensors; tensor_index++ ) {
        mpack_node_t output_node = mpack_node_map_value_at( outputs_map, tensor_index );
        output_datas[tensor_index] = mpack_node_bin_data( output_node );
        output_sizes[tensor_index] = mpack_node_bin_size( output_node );
        output_names[tensor_index] = mpack_node_cstr_alloc( mpack_node_map_key_at( outputs_map, tensor_index ), 1024 );
    }

    ////////////////////////////////////////////////////
    //// Add extra output
    ////////////////////////////////////////////////////

    size_t number_outputs = num_tensors + 1;
    // Add output name
    static const char key_string[] = "C-MsgPack-Socket-Postprocessor";
    output_names = realloc( output_names, sizeof( char * ) * number_outputs );
    output_names[number_outputs - 1] = malloc( sizeof( char ) * ( STRLEN( key_string ) ) );
    strcpy( output_names[number_outputs - 1], key_string );
    // Add output data
    output_datas = realloc( output_datas, sizeof( char * ) * number_outputs );
    output_datas[number_outputs - 1] = "Processed";
    // Add output size
    output_sizes = realloc( output_sizes, sizeof( size_t ) * number_outputs );
    output_sizes[number_outputs - 1] = 9;
    // Add output rank
    output_ranks = realloc( output_ranks, sizeof( int32_t ) * number_outputs );
    output_ranks[number_outputs - 1] = 1;
    // Add output shape
    output_shapes = realloc( output_shapes, sizeof( int64_t * ) * number_outputs );
    output_shapes[number_outputs - 1] = malloc( sizeof( int64_t ) * 1 );
    output_shapes[number_outputs - 1][0] = 9;
    // Add output data type
    // 1:  //FLOAT
    // 2:  //UINT8
    // 3:  //INT8
    // 4:  //UINT16
    // 5:  //INT16
    // 6:  //INT32
    // 7:  //INT64
    // 8:  //STRING
    // 9:  //BOOL
    // 11: //DOUBLE
    // 12: //UINT32
    // 13: //UINT64
    output_data_types = realloc( output_data_types, sizeof( int32_t ) * number_outputs );
    output_data_types[number_outputs - 1] = 8;

    ////////////////////////////////////////////////////
    //// Write output data
    ////////////////////////////////////////////////////

    // Initialize writer
    mpack_writer_t writer;
    char *mpack_buffer;
    size_t buffer_size;
    mpack_writer_init_growable( &writer, &mpack_buffer, &buffer_size );

    // Start building root map
    mpack_start_map( &writer, 4 );

    // Write outputs ({OutputName} bin)
    // Map key
    mpack_write_cstr( &writer, "Outputs" );
    // Map value
    mpack_start_map( &writer, number_outputs );
    for ( int index = 0; index < number_outputs; index++ ) {
        mpack_write_cstr( &writer, output_names[index] );
        mpack_write_bin( &writer, (const char *) output_datas[index], output_sizes[index] );
    }
    mpack_finish_array( &writer );// Finish "Outputs" array

    // Write output ranks ([num tensors]i32)
    // Map key
    mpack_write_cstr( &writer, "OutputRanks" );
    // Map value
    mpack_start_array( &writer, number_outputs );
    for ( int index = 0; index < number_outputs; index++ ) {
        mpack_write_i32( &writer, output_ranks[index] );
    }
    mpack_finish_array( &writer );// Finish "OutputRanks" array

    // Write output shapes ([num tensors][rank]i64)
    // Map key
    mpack_write_cstr( &writer, "OutputShapes" );
    // Map value
    mpack_start_array( &writer, number_outputs );
    for ( int output_index = 0; output_index < number_outputs; output_index++ ) {
        mpack_start_array( &writer, output_ranks[output_index] );
        for ( int rank_index = 0; rank_index < output_ranks[output_index]; rank_index++ ) {
            mpack_write_i64( &writer, output_shapes[output_index][rank_index] );
        }
        mpack_finish_array( &writer );// Finish "OutputShapes" inner array
    }
    mpack_finish_array( &writer );// Finish "OutputShapes" outer array

    // Write output data types ([num tensors]i32)
    // Map key
    mpack_write_cstr( &writer, "OutputDataTypes" );
    // Map value
    mpack_start_array( &writer, number_outputs );
    for ( int index = 0; index < number_outputs; index++ ) {
        mpack_write_i32( &writer, output_data_types[index] );
    }
    mpack_finish_array( &writer );// Finish "OutputDataTypes" array

    // Finish building root map
    mpack_finish_map( &writer );

    // Clean up memory
    free( output_ranks );
    for ( int index = 0; index < number_outputs; index++ ) {
        free( output_shapes[index] );
    }
    free( output_shapes );
    free( output_data_types );
    for ( int index = 0; index < number_outputs; index++ ) {
        free( output_names[index] );
    }
    free( output_names );
    free( output_datas );
    free( output_sizes );

    // Finish writing
    if ( mpack_writer_destroy( &writer ) != mpack_ok ) {
        fprintf( stderr, "An error occurred encoding the data!\n" );
        // Free buffer since it was not succesful
        free( writer.buffer );
        return NULL;
    }

    *output_buffer_length = buffer_size;

    return (char *) mpack_buffer;
}

// Function to handle interrupt signals
void handle_interrupt( int signal ) {
    // Set the interrupt flag to true on receiving an interrupt signal
    interrupt_flag = true;
}