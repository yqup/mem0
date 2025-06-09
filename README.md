📄 crewai_load_pdf.py

This script simplifies loading PDF content into Mem0, making it available for CrewAI agents to recall and utilise.

⸻

🔍 What it does
	•	Extracts text from a PDF file
	•	Encodes content into embeddings using Mem0
	•	Stores the embeddings in a searchable memory store
	•	Enables CrewAI agents to retrieve info when needed

⸻

🛠️ Requirements
	•	Python 3.10+
	•	Install dependencies:

pip install mem0ai crewai pypdf



⸻

⚙️ Usage

python crewai_load_pdf.py \
  --pdf-path /path/to/file.pdf \
  --mem0-endpoint http://localhost:8000 \
  --user-id user123

Arguments:

Option	Description
--pdf-path	Path to your local PDF file
--mem0-endpoint	Mem0 API base URL (e.g. http://localhost:8000)
--user-id	Identifier under which memory is stored


⸻

✨ How it works
	1.	Reads the PDF using pypdf
	2.	Splits into text chunks (configurable size)
	3.	Creates embeddings with Mem0 AI SDK
	4.	Saves them under the specified user ID

⸻

📦 Integration with CrewAI

Once loaded, use inside your CrewAI setup:

from crewai import Agent, Crew, Task
from crewai_tools import Mem0Tool  # hypothetical tool

agent = Agent(
    role="Researcher",
    tools=[Mem0Tool(user_id="user123", endpoint="http://localhost:8000")]
)

# Inside your task, agent can query memory:
# mem0.search("What does the PDF say about X?")


⸻

🚧 Notes
	•	Adjust chunk size for performance vs recall
	•	Ensure Mem0 service is running before executing
	•	PDF parsing may struggle with complex layouts (e.g. tables)

⸻

✅ To do
	•	Add support for directory of PDFs
	•	Use async loading for large files
	•	Include logging and retry logic for robustness

