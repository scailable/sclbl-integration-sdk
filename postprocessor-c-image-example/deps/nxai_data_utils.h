#pragma once

#include "nxai_data_structures.h"

#include <stddef.h>
#include <stdint.h>

#include "mpack.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Writes inference results, bounding boxes, scores, and counts to a buffer.
 *
 * This function initializes an mpack writer, copies data from the inference results root node
 * to the writer, and then writes additional data (bounding boxes, scores, counts) to the writer.
 * It excludes certain keys ("BBoxes_xyxy", "Scores", "Counts") from the copied data.
 * Finally, it completes the writing process and returns the buffer containing the serialized data.
 *
 * @param inference_results_root The root node of the inference results.
 * @param num_bboxes The number of bounding boxes.
 * @param bboxes Pointer to an array of bounding box objects.
 * @param num_scores The number of scores.
 * @param scores Pointer to an array of score objects.
 * @param num_counts The number of counts.
 * @param counts Pointer to an array of count objects.
 * @param return_buffer_size Pointer to a size_t variable where the size of the returned buffer will be stored.
 * @return A pointer to the buffer containing the serialized data, or NULL if an error occurred.
 */
char *nxai_write_buffer( mpack_node_t inference_results_root, size_t num_bboxes, bbox_object_t *bboxes, size_t num_scores, score_object_t *scores, size_t num_counts, count_object_t *counts, size_t *return_buffer_size );

#ifdef __cplusplus
}
#endif
