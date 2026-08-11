"""
Insurance AI Agent.

Creates a LangChain-based AI Agent that can use
insurance-related tools and maintain conversation
memory during the current session.
"""

from langchain_ollama import ChatOllama

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage
)

from tools.insurance_tools import create_user_tools
from memory.conversation_memory import ConversationMemory
from memory.conversation_summary import ConversationSummary


RECENT_MESSAGE_LIMIT = 6
SUMMARY_THRESHOLD = 10

class InsuranceAgent:
    """
    Insurance AI Agent for authenticated customers.
    """
   
    def __init__(self, session):

        self.session = session
        self.customer_id = session.get_user_id()

        self.conversation_memory = ConversationMemory(
            self.customer_id
        )

        self.llm = ChatOllama(
            model="qwen2.5",
            temperature=0
        )

        # Create tools restricted to authenticated user.
        self.tools = create_user_tools(
            session
        )

        # Bind tools to LLM.
        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )

        # -----------------------------------------
        # Load persistent conversation memory
        # -----------------------------------------
        
        self.conversation_summary = ConversationSummary(
                    self.customer_id
                )
        self.summary = (
        self.conversation_summary.get_summary()
        )
        
        print("\n========== SUMMARY DEBUG ==========")
        print("Customer ID:", self.customer_id)
        print("Summary:", self.summary)
        print("Summary exists:", bool(self.summary))
        print("===================================\n")

        # Load only recent conversation
        self.conversation_history = (
            self.load_recent_conversation_history()
        )

        # self.conversation_history = (
        #     self.load_conversation_history()
        # )
        
    def generate_conversation_summary(self):

            if not self.conversation_history:
                return None

            conversation_text = ""

            for message in self.conversation_history:

                if isinstance(message, HumanMessage):

                    conversation_text += (
                        f"Customer: {message.content}\n"
                    )

                elif isinstance(message, AIMessage):

                    conversation_text += (
                        f"Assistant: {message.content}\n"
                    )

            prompt = f"""
        You are an AI memory summarization system
        for an insurance company.

        Summarize the following customer conversation.

        Keep only important information that may be
        useful in future conversations.

        Include:

        - Insurance topics discussed
        - Policy information discussed
        - Claim information discussed
        - Important customer requests
        - Important decisions or outcomes

        Do not invent information.

        Conversation:

        {conversation_text}

        Create a concise summary.
        """

            print("\nGenerating conversation summary...")

            response = self.llm.invoke(
                prompt
            )

            summary = response.content

            print("\n========== GENERATED SUMMARY ==========")
            print(summary)
            print("=======================================\n")

            return summary   
    
    def save_conversation_summary(self):

        summary = self.generate_conversation_summary()

        if summary:

            self.conversation_summary.save_summary(
                summary
            )

            # Update in-memory persistent summary
            self.summary = summary

            print(
                "Conversation summary saved to PostgreSQL."
            )
        
                
    def load_conversation_summary(self):

        summary = self.conversation_summary.get_summary()

        if summary:

            print("\n========== CONVERSATION SUMMARY ==========")
            print(summary)
            print("==========================================\n")

        return summary
    
    def should_summarize(self):

        return (
            len(self.conversation_history)
            >= SUMMARY_THRESHOLD
        )
    
    def reset_recent_conversation(self):

        # Keep only the latest 6 messages
        self.conversation_history = (
            self.conversation_history[
                -RECENT_MESSAGE_LIMIT:
            ]
        )

        print(
            "\nRecent conversation memory "
            "rotated."
        )

        print(
            "Messages retained:",
            len(self.conversation_history)
        )
        
    def load_conversation_history(self):

        rows = self.conversation_memory.load_messages()

        print("\n========== LOADED MEMORY ==========")
        print("Customer ID:", self.customer_id)
        print("Rows loaded:", len(rows))

        for row in rows:
            print("ROW:", row)

        print("===================================\n")

        history = []

        for role, content in rows:

            if role == "user":

                history.append(
                    HumanMessage(
                        content=content
                    )
                )

            elif role == "assistant":

                history.append(
                    AIMessage(
                        content=content
                    )
                )

        print(
            "Conversation history messages:",
            len(history)
        )

        return history

    def update_conversation_summary(self):

        if not self.should_summarize():

            return

        print(
            "\nConversation history reached "
            "summary threshold."
        )

        print(
            "\nGenerating conversation summary..."
        )

        self.save_conversation_summary()

        # Rotate short-term memory
        self.reset_recent_conversation()
    
    def load_recent_conversation_history(self):

        rows = self.conversation_memory.load_recent_messages(
            limit=6
        )

        history = []

        for role, content in rows:

            if role == "user":

                history.append(
                    HumanMessage(
                        content=content
                    )
                )

            elif role == "assistant":

                history.append(
                    AIMessage(
                        content=content
                    )
                )

        print(
            "\nRecent conversation messages:",
            len(history)
        )

        return history

    def invoke(self, user_message):
        """
        Process user message while maintaining
        short-term and persistent conversation history.
        """

        # -----------------------------------------
        # System instructions
        # -----------------------------------------

        system_prompt = """
        You are an Insurance AI Assistant.

        The customer is already authenticated.

        You may only provide information belonging
        to the currently authenticated customer.

        Available tools are restricted to the
        authenticated customer.

        IMPORTANT SECURITY RULES:

        1. Never retrieve another customer's information.

        2. Never attempt to change the authenticated
        customer's identity.

        3. Never ask the user for another customer ID
        to retrieve information.

        4. If the user asks for another customer's
        policy, claim, or personal information,
        refuse the request.

        5. Do not claim that you will retrieve another
        customer's information.

        6. Use tools only for the authenticated customer.

        7. Never invent information.

        8. All monetary values returned by tools are
        Malaysian Ringgit (RM).

        9. Use conversation history to understand
        follow-up questions.

        10. Answer the user's actual question directly.
        """

        # -----------------------------------------
        # Build messages
        # -----------------------------------------

        messages = [
            SystemMessage(
                content=system_prompt
            )
        ]

        # -----------------------------------------
        # Add persistent conversation summary
        # -----------------------------------------

        if self.summary:

            print("\n========== PERSISTENT SUMMARY ==========")
            print(self.summary)
            print("========================================\n")
            messages.append(
                SystemMessage(
                    content=f"""
            Previous conversation summary:

            {self.summary}

            IMPORTANT MEMORY RULES:

            1. The current user question is the highest priority.

            2. Use the previous conversation summary only
            to understand context and follow-up questions.

            3. Do NOT assume that the user is asking about
            the last topic mentioned in the summary.

            4. Identify the intent of the CURRENT user question
            before answering.

            5. If the current question asks about the policy,
            answer about the policy.

            6. If the current question asks about claims,
            answer about claims.

            7. If the current question refers to something
            previously discussed, use the summary to
            resolve that reference.

            8. Never replace the current question with an
            older question.

            9. Never invent information.

            10. All monetary values are Malaysian Ringgit (RM).

            Use the summary as background memory, not as the
            current user request.
            """
                )
            )

        # -----------------------------------------
        # Add recent conversation
        # -----------------------------------------

        messages.extend(
            self.conversation_history
        )
        
        # -----------------------------------------
        # Add current user message
        # -----------------------------------------

        messages.append(
            HumanMessage(
                content=user_message
            )
        )

        # -----------------------------------------
        # First LLM call
        # -----------------------------------------

        print("\nLLM Thinking...")

        response = self.llm_with_tools.invoke(
            messages
        )

        print(
            "Tool Calls:",
            response.tool_calls
        )

        # =================================================
        # CASE 1: LLM does NOT need a tool
        # =================================================

        if not response.tool_calls:

            # -----------------------------------------
            # Save to short-term memory
            # -----------------------------------------

            self.conversation_history.extend([
                HumanMessage(
                    content=user_message
                ),
                response
            ])

            # -----------------------------------------
            # Save to PostgreSQL
            # -----------------------------------------

            self.conversation_memory.save_message(
                "user",
                user_message
            )

            self.conversation_memory.save_message(
                "assistant",
                response.content
            )

            # Check conversation summary
            self.update_conversation_summary()
    
            return response.content

        # =================================================
        # CASE 2: LLM requested one or more tools
        # =================================================

        messages.append(
            response
        )

        # -----------------------------------------
        # Execute requested tools
        # -----------------------------------------

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(
                "\nSelected Tool:",
                tool_name
            )

            print(
                "Arguments:",
                tool_args
            )

            selected_tool = None

            # Find requested tool
            for tool in self.tools:

                if tool.name == tool_name:

                    selected_tool = tool
                    break

            # Tool not found
            if selected_tool is None:

                return (
                    f"Tool '{tool_name}' "
                    f"was not found."
                )

            # -----------------------------------------
            # Execute tool
            # -----------------------------------------

            tool_result = selected_tool.invoke(
                tool_args
            )

            print(
                "Tool Result:",
                tool_result
            )

            # -----------------------------------------
            # Add tool result to current LLM messages
            # -----------------------------------------

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"]
                )
            )

        # =================================================
        # Second LLM call
        # =================================================

        final_response = (
            self.llm_with_tools.invoke(
                messages
            )
        )

        # -----------------------------------------
        # Save to short-term memory
        # -----------------------------------------

        self.conversation_history.append(
            HumanMessage(
                content=user_message
            )
        )

        # Save AI tool-call message
        self.conversation_history.append(
            response
        )

        # Save tool results to short-term memory
        for message in messages:

            if isinstance(
                message,
                ToolMessage
            ):

                self.conversation_history.append(
                    message
                )

        # Save final AI response
        self.conversation_history.append(
            final_response
        )

        # -----------------------------------------
        # Save USER message to PostgreSQL
        # -----------------------------------------

        self.conversation_memory.save_message(
            "user",
            user_message
        )

        # -----------------------------------------
        # Save FINAL ASSISTANT response to PostgreSQL
        # -----------------------------------------

        self.conversation_memory.save_message(
            "assistant",
            final_response.content
        )
        
        # if self.should_summarize():
        #     self.save_conversation_summary()
        
        # -----------------------------------------
        # Check conversation summary
        # -----------------------------------------

        self.update_conversation_summary()

        return final_response.content