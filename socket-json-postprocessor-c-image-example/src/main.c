// Standard system includes
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

// Local includes
#include "sclbl_socket_utils.h"
#include "yyjson.h"

// Flag to keep track of interrupts
volatile sig_atomic_t interrupt_flag = false;

/**
 * @brief A function to process the Json document received from the Scailable Runtime and returns a modified JSON.
 *
 * This is the function you are likely to replace with your own code. For this example the function adds an
 * additional field to the JSON's "output" object and returns the result.
 *
 * @param input_document The json parsed document
 * @return char* The modified json string
 */
static char *processJSONDocument( yyjson_doc *input_document );
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

        // Parse input buffer into a JSON document
        yyjson_doc *input_doc = yyjson_read( input_buffer, (size_t) message_length, 0 );

        // Process the JSON document
        char *output_string = processJSONDocument( input_doc );

        // Free the input document after processing
        yyjson_doc_free( input_doc );

        // Send the processed output back to the socket
        sclbl_socket_send_to_connection( connection_fd, output_string, (uint32_t) strlen( output_string ) );

        // Close the connection
        if ( close( connection_fd ) == -1 ) {
            fprintf( stderr, "EXAMPLE POSTPROCESSOR: Warning: Sender socket close error!\n" );
        }
    }

    printf( "EXAMPLE POSTPROCESSOR: Exiting.\n" );
}

// Function to process a JSON document
char *processJSONDocument( yyjson_doc *input_document ) {
    // Get the root of the JSON document
    yyjson_val *document_root = yyjson_doc_get_root( input_document );

    // Get the "output" object from the JSON document
    yyjson_val *output_object = yyjson_obj_get( document_root, "output" );

    printf( "EXAMPLE POSTPROCESSOR: Received document output object has keys:\n" );

    // Loop over the keys in the "output" object and print them
    size_t idx, max;
    yyjson_val *key, *val;
    yyjson_obj_foreach( output_object, idx, max, key, val ) {
        printf( "\tEXAMPLE POSTPROCESSOR: %s\n", yyjson_get_str( key ) );
    }

    // Create a mutable copy of the input document
    yyjson_mut_doc *mut_doc = yyjson_doc_mut_copy( input_document, NULL );

    // Get the mutable "output" object from the mutable copy
    yyjson_mut_val *root_mut = yyjson_mut_doc_get_root( mut_doc );
    yyjson_mut_val *output_object_mut = yyjson_mut_obj_get( root_mut, "output" );

    // Add a new key-value pair to the "output" object
    yyjson_mut_obj_add_str( mut_doc, output_object_mut, "examplePostProcessor", "Processed" );

    // Convert the mutable document back to a string
    char *output_document = yyjson_mut_write( mut_doc, 0, NULL );

    // Free the mutable document
    yyjson_mut_doc_free( mut_doc );

    return output_document;
}

// Function to handle interrupt signals
void handle_interrupt( int signal ) {
    // Set the interrupt flag to true on receiving an interrupt signal
    interrupt_flag = true;
}