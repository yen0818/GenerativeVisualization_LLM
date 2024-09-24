import json, re
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    response = extract_final_answer(response)
    response = response.strip() 
    print(f"Response: {response}")
    ### ADDED this loop to overcome the false Dictionaries load/loads creates!  ####
    if type(response) == str:
        return json.loads(response)
    else:
        return response
    
def extract_final_answer(output: str) -> str:
    """
    Extract the 'Final Answer' from the agent's output.

    Args:
        output (str): The output string from the agent.

    Returns:
        str: The final answer extracted from the output.
    """
    match = re.search(r'Final Answer:\s*(.*)', output)
    if match:
        return match.group(1).strip()
    return output

    
def write_answer(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """

    # Check if the response is an answer.
    if "answer" in response_dict:
        st.session_state.messages.append({"role": "assistant", "content": response_dict["answer"]})
        st.write(response_dict["answer"])

    # Check if the response is a bar chart.
    if "bar" in response_dict:
        st.session_state.messages.append({"role": "assistant", "content": response_dict["bar"]})
        data = response_dict["bar"]
        try:
            columns = data['columns']
            values = data['data']

            # Create the combined bar chart
            fig = go.Figure()

            # Plot each column's data in the chart
            # Add bar traces for each column
            if isinstance(values[0], list):
                # Handle the list of lists case
                for i, column in enumerate(columns):
                    column_values = [row[i] for row in values]
                    print(f"Column: {column}, Values: {values}")
                    # Add bar trace
                    fig.add_trace(go.Bar(
                        x=list(range(1, len(column_values) + 1)),  # x-axis as index (1, 2, 3, ...)
                        y=column_values,  # y-axis as the values for this column
                        name=column  # Name the trace after the column
                    ))
            else:
                # Handle the flat list case
                fig.add_trace(go.Bar(
                    x=list(range(1, len(values) + 1)),  # x-axis as index (1, 2, 3, ...)
                    y=values,  # y-axis as the values for this column
                    name=columns  # Name the trace after the column
                ))

            # Assuming columns is a variable that might be a list
            if isinstance(columns, list):
                columns = ', '.join(columns)
                
            # Add title and labels
            fig.update_layout(
                title=f'Bar Chart for {columns}',
                xaxis_title='Index',
                yaxis_title=columns,
                barmode='group'  # This displays bars side by side
            )

            st.plotly_chart(fig)

            # st.bar_chart(df)
        except Exception as e:
            print(f"Couldn't create bar chart from data")
            print(f"Error: {e}")
            st.write(f"Couldn't create bar chart from data")

# Check if the response is a line chart.
    if "line" in response_dict:
        st.session_state.messages.append({"role": "assistant", "content": response_dict["line"]})
        data = response_dict["line"]
        try:
            # Check if data is a flat list of floats
            if isinstance(data['data'][0], float):
                # Create DataFrame directly
                df_data = {data['columns'][0]: data['data']}
            else:
                # If data is a list of lists
                df_data = {col: [x[i] for x in data['data']] for i, col in enumerate(data['columns'])}
            df = pd.DataFrame(df_data)

            st.line_chart(df)
        except ValueError:
            print(f"Couldn't create DataFrame from data: {data}")


    # Check if the response is a table.
    if "table" in response_dict:
        print("###TABLE")
        data = response_dict["table"]
        try:
            df = pd.DataFrame(data["data"], columns=data["columns"])
            st.table(df)
        except Exception as e:
            print(f"Couldn't create table from data")
            print(f"Error: {e}")
            st.write(f"Couldn't create table from data")

    