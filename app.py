import streamlit as st
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
import ast

# ✅ Initialize Memory in Session State
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# ✅ Initialize Chat Model Securely
chat = ChatGroq(temperature=0.7, model_name="llama3-70b-8192", groq_api_key="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") 

# ✅ Query AI Model
def query_llama3(user_query):
    topic = "Intigration"
    """Handles user queries while retrieving past chat history, then evaluates the response."""
    
    system_prompt = """
    System Prompt: You are an expert educational assessment generator trained provide engaging multiple-choice questions (MCQs) for enterprise-level adaptive learning systems on the topic {topic}. Your task is to:

    Analyze given educational content and generate MCQs that are relevant to the topic and appropriate in difficulty.
    The questions should be accurate and not based on your imagination.
    Generate four answer choices for each question (A, B, C, D), ensuring that only one is correct and others are plausible distractors.
    Mark the correct answer clearly using the format: [Que, A, B, C, D, Ans], where Que is the question, ABCD are the options, and Ans is the correct answer.
    Adapt content dynamically - make questions easier or harder based on user performance (if performance trends are provided).
    Ensure quality - Questions must be clear, grammatically correct, and intuitive for users to navigate through.
    Maintain UI-friendly structure - The format should be clean and suitable for integration into frontend interfaces. 
    give the output in the form of a python list, only a list nothing more.
    ensure that every given nested list has 6 elements.
    For True or False questions only give 2 options
    """

    past_chat = st.session_state.memory.load_memory_variables({}).get("chat_history", [])

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Past Chat: {past_chat}\n\nUser: {user_query}")
    ]

    try:
        response = chat.invoke(messages)
        print("Qusetions : ",response.content,"\n\n")
        st.session_state.memory.save_context({"input": user_query}, {"output": response.content})
        return response.content if response else "⚠️ No response."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ✅ Streamlit Page Configuration

# ✅ Set Page Config
st.set_page_config(page_title="MCQ Generator", page_icon="🤖", layout="wide")

# ✅ Apply Dark Theme Styling
st.markdown("""
<style>
/* Set Dark Background */
body {
    background-color: #121212;
    color: #E0E0E0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Chat Container */
.chat-container {
    margin: 20px;
}

/* Common Chat Bubble Style */
.chat-bubble {
    padding: 12px 18px;
    border-radius: 15px;
    margin-bottom: 10px;
    max-width: 75%;
    line-height: 1.5;
    font-size: 16px;
}

/* User Message Styling */
.user-bubble {
    background-color: #1E88E5;
    color: white;
    margin-left: auto;
    text-align: right;
    border-top-right-radius: 0px;
}

/* Assistant Message Styling */
.assistant-bubble {
    background-color: #333333;
    color: #E0E0E0;
    margin-right: auto;
    text-align: left;
    border-top-left-radius: 0px;
}

/* Center the Title */
.title-container {
    text-align: center;
    font-size: 64px;
    font-weight: bold;
    margin-top: 10px;
}

/* Input Box Customization */
.stChatInput {
    background-color: #333333 !important;
    color: white !important;
    border: 1px solid #555555 !important;
}
</style>
""", unsafe_allow_html=True)

# ✅ Title Section
st.markdown("<div class='title-container'>🤖 <b>MCQ Generator</b></div>", unsafe_allow_html=True)

# ✅ Add Topic Input Box and Button
if "current_question" in st.session_state:
    topic = st.session_state.topic
    generate_button = st.session_state.generate_button  

if "current_question" not in st.session_state:
    print("initialized")
    topic = st.text_input("Enter Topic:", key="topic_input")
    generate_button = st.button("Generate MCQ")
    st.session_state.topic = topic
    st.session_state.generate_button = generate_button
    st.session_state.once = True

if st.session_state.once and topic and generate_button:
    st.session_state.questions = ast.literal_eval(query_llama3(topic))
    st.session_state.total = len(st.session_state.questions)
    st.session_state.once = False
    st.session_state.done = False
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.answers = []
    print(st.session_state.total)

# Initialize session state for tracking progress if not already initialized
# Show MCQ and handle answer selection

if generate_button and topic :

    if st.session_state.done == False:
        # Generate MCQs when the button is clicked
        st.session_state.answers = []
        print("pressed button")
        print("Current question : ",st.session_state.current_question,"  topic : ",topic,"   generator button : ",generate_button, "Score : ",st.session_state.score)
        
        # Get the current question
        question_data = st.session_state.questions[st.session_state.current_question]
        question = question_data[0]
        options = question_data[1:-1]
        correct_answer = question_data[-1]

        # Display the current question
        st.markdown(f"**{question}**")
        
        # Present answer choices using buttons
        answer = None
        button_keys = [f"answer_{i}_{st.session_state.current_question}" for i in range(4)]  # Create unique keys for each button
        for i, option in enumerate(options):
            if st.button(option, key=button_keys[i]):
                answer = option
                print("Answer : ",answer)
                # Store the user's answer in session state
                if len(st.session_state.answers) <= st.session_state.current_question:
                    st.session_state.answers.append(answer)
                    print("\nAppended answer \nAnswer :",st.session_state.answers,"   Correct answer : ",correct_answer)

        if answer != None:
            # Increment question index if there's more
            if st.session_state.answers[0] == correct_answer:
                print("Correct")
                st.session_state.score += 1
            if st.session_state.current_question < st.session_state.total -1:
                print("Next question")
                st.session_state.current_question += 1
                st.rerun()  # Refresh to show next question
            else:
                st.session_state.done = True
                st.rerun()
    else: 
        st.markdown("You've completed the test! Here's your summary:")
        correct_answers = sum([1 for ans, correct in zip(st.session_state.answers, [q[-1] for q in st.session_state.questions]) if ans == correct])
        total_questions = len(st.session_state.answers)
        st.write(f"You score is {st.session_state.score} out of {st.session_state.total}.")
        if st.button("New Test"):
            st.session_state.clear()
            st.rerun()  # Optional: Refresh the app to reflect the cleared state
