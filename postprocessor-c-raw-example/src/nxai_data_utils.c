#include "nxai_data_utils.h"

#include "mpack.h"

/**
 * @brief Writes the scores to the mpack writer.
 *
 * This function iterates over the scores array and writes each score along with its class name to the mpack writer.
 * If a class name is not provided, it defaults to "unknown".
 *
 * @param scores Pointer to an array of score_object_t structures containing the scores.
 * @param num_scores The number of scores in the scores array.
 * @param writer Pointer to the mpack_writer_t structure where the scores will be written.
 */
static void write_scores( score_object_t *scores, size_t num_scores, mpack_writer_t *writer ) {
    if ( scores == NULL ) {
        // No scores to write
        return;
    }
    // Write BBoxes map
    // Map key
    mpack_write_cstr( writer, "Scores" );
    // Map value
    mpack_start_map( writer, num_scores );

    // Write each score into map, with the class names as key
    for ( size_t class_index = 0; class_index < num_scores; class_index++ ) {
        // Map key
        if ( scores[class_index].class_name != NULL ) {
            mpack_write_cstr( writer, scores[class_index].class_name );
        } else {
            mpack_write_cstr( writer, "unkown" );
        }
        // Map value
        mpack_write_float( writer, scores[class_index].score );
    }

    mpack_finish_map( writer );// Finish "Scores" map
}

/**
 * @brief Writes the counts to the mpack writer.
 *
 * This function iterates over the counts array and writes each count along with its class name to the mpack writer.
 * If a class name is not provided, it defaults to "unknown".
 *
 * @param counts Pointer to an array of count_object_t structures containing the counts.
 * @param num_counts The number of counts in the counts array.
 * @param writer Pointer to the mpack_writer_t structure where the counts will be written.
 */
static void write_counts( count_object_t *counts, size_t num_counts, mpack_writer_t *writer ) {
    if ( counts == NULL ) {
        // No counts to write
        return;
    }
    // Write BBoxes map
    // Map key
    mpack_write_cstr( writer, "Counts" );
    // Map value
    mpack_start_map( writer, num_counts );

    // Write each count into map, with the class names as key
    for ( size_t class_index = 0; class_index < num_counts; class_index++ ) {
        // Map key
        if ( counts[class_index].class_name != NULL ) {
            mpack_write_cstr( writer, counts[class_index].class_name );
        } else {
            mpack_write_cstr( writer, "unkown" );
        }
        // Map value
        mpack_write_u64( writer, counts[class_index].count );
    }

    mpack_finish_map( writer );// Finish "Counts" map
}

/**
 * @brief Writes the bounding boxes to the mpack writer.
 *
 * This function iterates over the bboxes array and writes each bounding box along with its class name to the mpack writer.
 * It only writes bounding boxes with the "xyxy" format. If a class name is not provided, it defaults to "unknown".
 *
 * @param bboxes Pointer to an array of bbox_object_t structures containing the bounding boxes.
 * @param num_bboxes The number of bounding boxes in the bboxes array.
 * @param writer Pointer to the mpack_writer_t structure where the bounding boxes will be written.
 */
static void write_bboxes( bbox_object_t *bboxes, size_t num_bboxes, mpack_writer_t *writer ) {

    if ( bboxes == NULL ) {
        // No bboxes to write
        return;
    }
    // Write BBoxes map
    // Map key
    mpack_write_cstr( writer, "BBoxes_xyxy" );
    // Map value
    mpack_start_map( writer, num_bboxes );

    // Write each bbox into map, with the class names as key
    for ( size_t class_index = 0; class_index < num_bboxes; class_index++ ) {
        if ( strcmp( bboxes[class_index].format, "xyxy" ) != 0 ) {
            continue;
        }
        // Map key
        if ( bboxes[class_index].class_name != NULL ) {
            mpack_write_cstr( writer, bboxes[class_index].class_name );
        } else {
            mpack_write_cstr( writer, "unkown" );
        }
        // Map value
        mpack_write_bin( writer, (char *) bboxes[class_index].coordinates, bboxes[class_index].length * sizeof( float ) );
    }

    mpack_finish_map( writer );// Finish "BBoxes_xyxy" map
}

/**
 * @brief Recursively copies data from an mpack node to an mpack writer.
 *
 * This function is used to recursively copy data from an mpack node to an mpack writer.
 * It handles different types of data (bool, int, uint, float, double, str, bin, array, map)
 * and writes them to the writer.
 *
 * @param node The mpack node containing the data to be copied.
 * @param writer The mpack writer to which the data will be written.
 */
static void copy_mpack_buffer_recursive( mpack_node_t node, mpack_writer_t *writer ) {
    mpack_type_t node_type = mpack_node_type( node );
    switch ( node_type ) {
        case mpack_type_bool: {
            mpack_write_bool( writer, mpack_node_bool( node ) );
            break;
        }
        case mpack_type_uint:
            mpack_write_u64( writer, mpack_node_u64( node ) );
            break;
        case mpack_type_int:
            mpack_write_i64( writer, mpack_node_i64( node ) );
            break;
        case mpack_type_float:
            mpack_write_float( writer, mpack_node_float( node ) );
            break;
        case mpack_type_double:
            mpack_write_double( writer, mpack_node_double( node ) );
            break;
        case mpack_type_str: {
            const char *string = mpack_node_str( node );
            size_t string_length = mpack_node_strlen( node );
            mpack_write_str( writer, string, (uint32_t) string_length );
            break;
        }
        case mpack_type_bin: {
            mpack_write_bin( writer, mpack_node_bin_data( node ), mpack_node_bin_size( node ) );
            break;
        }
        case mpack_type_array: {
            size_t arr_length = mpack_node_array_length( node );
            mpack_start_array( writer, arr_length );
            for ( size_t arr_index = 0; arr_index < arr_length; arr_index++ ) {
                copy_mpack_buffer_recursive( mpack_node_array_at( node, arr_index ), writer );
            }
            mpack_finish_array( writer );
            break;
        }
        case mpack_type_map: {
            size_t map_length = mpack_node_map_count( node );
            mpack_build_map( writer );// Start map
            for ( size_t map_index = 0; map_index < map_length; map_index++ ) {
                mpack_node_t key_node = mpack_node_map_key_at( node, map_index );
                // Write map key
                copy_mpack_buffer_recursive( key_node, writer );
                // Write map value
                mpack_node_t value_node = mpack_node_map_value_at( node, map_index );
                copy_mpack_buffer_recursive( value_node, writer );
            }
            mpack_complete_map( writer );// Finish map
            break;
        }
        default:
            break;
    }
}

char *nxai_write_buffer( mpack_node_t inference_results_root, size_t num_bboxes, bbox_object_t *bboxes, size_t num_scores, score_object_t *scores, size_t num_counts, count_object_t *counts, size_t *return_buffer_size ) {
    // Initialize writer
    mpack_writer_t writer;
    char *mpack_buffer;
    size_t buffer_size;
    mpack_writer_init_growable( &writer, &mpack_buffer, &buffer_size );

    // Make a copy of the inference results root to new writer
    size_t map_length = mpack_node_map_count( inference_results_root );
    mpack_build_map( &writer );// Start map
    for ( size_t map_index = 0; map_index < map_length; map_index++ ) {
        mpack_node_t key_node = mpack_node_map_key_at( inference_results_root, map_index );
        // Exclude keys
        if ( mpack_node_type( key_node ) == mpack_type_str ) {
            const char *key_string = mpack_node_str( key_node );
            size_t key_length = mpack_node_strlen( key_node );
            if ( strncmp( key_string, "BBoxes_xyxy", key_length ) == 0 || strncmp( key_string, "Scores", key_length ) == 0 || strncmp( key_string, "Counts", key_length ) == 0 ) {
                continue;
            }
        }
        // Write map key
        copy_mpack_buffer_recursive( key_node, &writer );
        // Write map value
        mpack_node_t value_node = mpack_node_map_value_at( inference_results_root, map_index );
        copy_mpack_buffer_recursive( value_node, &writer );
    }

    // Write bboxes
    write_bboxes( bboxes, num_bboxes, &writer );

    // Write scores
    write_scores( scores, num_scores, &writer );

    // Write counts
    write_counts( counts, num_counts, &writer );

    mpack_complete_map( &writer );// Finish map

    // Finish writing
    if ( mpack_writer_destroy( &writer ) != mpack_ok ) {
        fprintf( stderr, "An error occurred encoding the data!\n" );
        printf( "Error: %s\n", mpack_error_to_string( mpack_writer_error( &writer ) ) );
        // Free buffer since it was not succesful
        free( writer.buffer );
        return NULL;
    }

    *return_buffer_size = buffer_size;
    return mpack_buffer;
}
