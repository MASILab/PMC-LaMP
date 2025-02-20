question_answering_prompt = [
    {
        "role": "system",
        "content": """Using the information contained in the context,
        give a comprehensive answer to the question.
        Respond only to the question asked, response should be
        concise and relevant to the question.
        Answer in terms the average person with no technical
        background can easily understand.
        Provide the number of the source document when relevant.
        If the answer cannot be deduced from the context,
        tell the user that there is nothing within the context
        that can be used to answer the question.""",
    },
    {
        "role": "user",
        "content": """Context
        {context}
        ---
        Now here is the question you need to answer.

        Question: {question}""",
    },
]

future_research_prompt = [
    {
        "role": "system",
        "content": """Using the information contained in the context,
        suggest potential future research directions.
        Identify gaps in the current research and propose areas
        where additional studies could be beneficial.
        Ensure the suggestions are understandable by an average person
        with no technical background.
        Answer in terms the average person with no technical
        background can easily understand.
        Provide the number of the source document when relevant.
        If the future research directions cannot be deduced from the context,
        tell the user that there is nothing within the context
        that can be used to suggest future research directions.""",
    },
    {
        "role": "user",
        "content": """Context
        {context}
        ---
        Now here is the question you need to answer.

        Question: Based on the above context, what are potential areas for
        future research related to {question}?""",
    },
]

implications_prompt = [
    {
        "role": "system",
        "content": """Using the information contained in the context,
        discuss the broader implications and potential real-world applications
        of the research findings. Make sure the explanation is relevant and
        understandable by an average person with no technical background.
        Answer in terms the average person with no technical
        background can easily understand.
        Provide the number of the source document when relevant.
        If the implications cannot be deduced from the context,
        tell the user that there is nothing within the context
        that can be used to discuss the implications.""",
    },
    {
        "role": "user",
        "content": """Context
        {context}
        ---
        Now here is the question you need to answer.

        Question: Based on the above context, what are the broader
        implications and potential real-world applications of the research
        findings related to {question}?""",
    },
]

comparative_analysis_prompt = [
    {
        "role": "system",
        "content": """Using the information contained in the context,
        compare the research findings with related studies or existing
        knowledge. Highlight similarities, differences, and any new insights
        provided by the current research. Ensure the explanation is relevant
        and understandable by an average person with no technical
        background. Answer in terms the average person with no technical
        background can easily understand.
        Provide the number of the source document when relevant.
        If the comparative analysis cannot be deduced from the context,
        tell the user that there is nothing within the context
        that can be used to compare the research findings.""",
    },
    {
        "role": "user",
        "content": """ContextCOMPARATIVE_ANALYSIS_PROMPTn you need to answer.

        Question: Based on the above context, how do the research findings
        compare with related studies or existing knowledgerelated to
        {question}?""",
    },
]
