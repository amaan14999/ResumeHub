from flask import Flask, request, jsonify
from utils.conversation_utils import (
    create_conversation_and_add_files,
    get_conversation_status,
    ask_question,
)

import os

app = Flask(__name__)

conversation_id = ""
document_id = []


def init_app(app):
    @app.route("/upload", methods=["POST"])
    def process_and_ask():
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Save the file temporarily
        filename = os.path.join(
            "temporary_directory", file.filename
        )  # Replace with your directory
        file.save(filename)
        # folder_path = "temporary_directory"

        with open(filename, "rb") as file_data:
            files = {file.filename: file_data}
            response = create_conversation_and_add_files(files)
            if not response or not response.ok:
                os.remove(filename)  # Clean up the file
                return jsonify({"error": "Failed to create conversation"}), 500
            conversation_id = response.json().get("id")
        print(f"Conversation created with id: {conversation_id}")

        # Get conversation status
        response_json, err = get_conversation_status(conversation_id)
        if err:
            os.remove(filename)  # Clean up the file
            print(f"Error occurred: {err}")
            return jsonify({"error": err}), 500

        # Ask a question
        query = "Process the provided resume PDF file and extract the following details in a structured JSON format: Candidate Overview: Summarize the candidate's profile, highlighting career aspirations or professional summary. Key Details: Include sections for Name, Email, Phone Number, Education (with dates and institutions), Experience (with job titles, companies, and duration), Skills (categorized if applicable), Projects (brief descriptions and roles played), Honors and Awards (with dates and awarding bodies).10 Important Questions: Based on the resume content, generate 10 insightful questions that would be relevant for an interview or further assessment of the candidate. These questions should pertain to the candidate's experience, skills, and accomplishments, aiming to elicit detailed responses about their professional journey and competencies."
        document_id.append(response_json.get("documents")[0].get("id"))
        print(f"Conversation id : {conversation_id}")
        print(f"Document id: {document_id}")
        print("worked till here")

        answer, err = ask_question(conversation_id, query, document_id)
        print("worked till here")
        if err:
            os.remove(filename)  # Clean up the file
            print(
                f"Error getting an answer for document with id {document_id}, error: {err}"
            )
            return jsonify({"error": err}), 500

        # Clean up the file after use
        os.remove(filename)

        print(f"Answer for document with id {document_id}: {answer}")
        return jsonify({"answer": answer})


# def init_app(app):
#     @app.route("/upload", methods=["POST"])
#     def process_and_ask():
#         if "file" not in request.files:
#             return jsonify({"error": "No file part in the request"}), 400
#         file = request.files["file"]
#         if file.filename == "":
#             return jsonify({"error": "No file selected"}), 400

#         # Save the file temporarily
#         filename = os.path.join(
#             "temporary_directory", file.filename
#         )  # Replace with your directory
#         file.save(filename)
#         folder_path = "temporary_directory"

#         # Read the file and create a conversation
#         files: Dict[Text, bytes] = {}
#         for file in os.listdir(folder_path):
#             complete_path = os.path.join(folder_path, file)
#             files[file] = open(complete_path, "rb")

#         response = create_conversation_and_add_files(files)
#         if response.ok:
#             resp_data = response.json()
#             conversation_id = resp_data.get("id")
#             if not conversation_id:
#                 print("Unable to create new conversation.")
#         # old logic
#         # with open(filename, "rb") as file_data:
#         #     files = {file.filename: file_data}
#         #     response = create_conversation_and_add_files(files)
#         #     if not response or not response.ok:
#         #         os.remove(filename)  # Clean up the file
#         #         return jsonify({"error": "Failed to create conversation"}), 500
#         #     conversation_id = response.json().get("id")
#         print(f"Conversation created with id: {conversation_id}")

#         # Get conversation status
#         response_json, err = get_conversation_status(conversation_id)
#         if err:
#             os.remove(filename)  # Clean up the file
#             print(f"Error occurred: {err}")
#             return jsonify({"error": err}), 500

#         # Ask a question
#         # Replace 'YOUR_QUERY' and 'DOCUMENT_ID' with actual logic to determine them
#         query = "Give the Name of the user"
#         document_id.append(response_json.get("documents")[0].get("id"))
#         print(f"Conversation id : {conversation_id}")
#         print(f"Document id: {document_id}")
#         print("worked till here")

#         answer, err = ask_question(conversation_id, query, document_id)
#         print("worked till here")
#         if err:
#             os.remove(filename)  # Clean up the file
#             print(
#                 f"Error getting an answer for document with id {document_id}, error: {err}"
#             )
#             return jsonify({"error": err}), 500

#         # Clean up the file after use
#         os.remove(filename)

#         print(f"Answer for document with id {document_id}: {answer}")
#         return jsonify({"answer": answer})
