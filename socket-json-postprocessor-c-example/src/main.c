// Standard system includes
#include <stdio.h>
#include <signal.h>

// Local includes
#include "yyjson.h"
#include "sclbl_socket_utils.h"

// Flag to keep track of interrupts
volatile sig_atomic_t interrupt_flag = false;

// Function forward declarations
char *processJSONDocument(yyjson_doc *input_document);
void handle_interrupt(int sig);

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("EXAMPLE POSTPROCESSOR: Started with incorrect command line arguments.\n");
        exit(2);
    }

    // Set signal handler to listen for interrupt signals
    signal(SIGINT, handle_interrupt);

    const char *socket_path = argv[1];

    printf("EXAMPLE POSTPROCESSOR: Starting up with socket path: %s.\n", socket_path);

    char *input_buffer = NULL;
    size_t allocated_buffer_size = 0;
    uint32_t message_length;

    int socket_fd = sclbl_socket_create_listener(socket_path);

    // While no interrupt signal received
    while (interrupt_flag == false)
    {
        int connection_fd = sclbl_socket_await_message(socket_fd, &allocated_buffer_size, &input_buffer, &message_length);

        if (connection_fd == -1)
        {
            // Connection timed out, continue to wait for message again.
            // Useful to test if program should terminate and break
            continue;
        }

        yyjson_doc *input_doc = yyjson_read(input_buffer, (size_t)message_length, 0);

        char *output_string = processJSONDocument(input_doc);

        // Free document
        yyjson_doc_free(input_doc);

        sclbl_socket_send_to_socket(connection_fd, output_string, (uint32_t)strlen(output_string));
    }

    printf("EXAMPLE POSTPROCESSOR: Exiting.\n");
}

char *processJSONDocument(yyjson_doc *input_document)
{
    // Print some debug information
    yyjson_val *document_root = yyjson_doc_get_root(input_document);

    yyjson_val *output_object = yyjson_obj_get(document_root, "output");

    printf("EXAMPLE POSTPROCESSOR: Received document output object has keys:\n");

    size_t idx, max;
    yyjson_val *key, *val;
    yyjson_obj_foreach(output_object, idx, max, key, val)
    {
        printf("\tEXAMPLE POSTPROCESSOR: %s\n", yyjson_get_str(key));
    }

    // Add some generic information to object
    yyjson_mut_doc *mut_doc = yyjson_doc_mut_copy(input_document, NULL);

    yyjson_mut_val *root_mut = yyjson_mut_doc_get_root(mut_doc);
    yyjson_mut_val *output_object_mut = yyjson_mut_obj_get(root_mut, "output");

    yyjson_mut_obj_add_str(mut_doc, output_object_mut, "examplePostProcessor", "Processed");

    // Write document to string
    char *output_document = yyjson_mut_write(mut_doc, 0, NULL);

    yyjson_mut_doc_free(mut_doc);

    return output_document;
}

void handle_interrupt(int signal)
{
    // Get rid of compile warnings
    (void)(signal);
    interrupt_flag = true;
}
