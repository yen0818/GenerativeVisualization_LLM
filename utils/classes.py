import ast 
import re

def extract_code(response):
    if "```python" in response:
        code_pattern = r"```python(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        if matches:
            return matches[0].strip()
    elif "```py" in response:
        code_pattern = r"```py(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        if matches:
            return matches[0].strip()
    return response

def format_response(response):
    try:
        if not isinstance(response, dict):
            response_dict = ast.literal_eval(response)
        else:
            response_dict = response
    except (ValueError, SyntaxError):
        # raise ValueError("Invalid response format. Response must be a dictionary or a string representation of a dictionary.")
        pattern = r'Final Answer: (.*)'
        # Search for the pattern in the input string
        match = re.search(pattern, response)
        
        if match:
            json_str = match.group(1)
            try:
                response_dict = ast.literal_eval(json_str)
                if "answer" in response_dict:
                    return "general", response_dict["answer"]
            except (ValueError, SyntaxError):
                return "general", json_str
        else:
            return "general", response
    
    res_type = response_dict.get("answer_type")
    res = response_dict.get("answer")

    if res_type in ["plot", "table"]:
        if "```python" in res:
            res = extract_code(res)
        res = res.replace("\\n", "\n").replace("\\'", "'").strip()

    return res_type, res


def run_request(agent_executor, user_query): # , key, alt_key

    response = agent_executor.invoke({"input": user_query})
    print(f"RESPONSE: {response}")
    llm_response = response["output"]
    res_type, res = format_response(llm_response)
    return res_type, res



