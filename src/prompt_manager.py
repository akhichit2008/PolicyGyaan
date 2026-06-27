from google import genai

# Internal Modules (Application-level)
from utils import process_indices


class PromptManager:
    def __init__(self,client:genai.Client,model:str="gemini-2.5-flash"):
        self.client = client
        self.model = model

    def policy_redirect_prompt(self,policy_title:str,current_user:list) -> str:
        # current_user = [profession,gender,age,status]
        prompt = f"For the policy {policy_title}, provide responses in the following format:\
	            Policy Overview: Details of policy {policy_title},\
	            Impact on You: Impact of {policy_title} on {current_user[0]},{current_user[1]},{current_user[2]},{current_user[3]}\
	            History: History of policy {policy_title},\
	            Key Benefits: Key benefits of policy {policy_title},\
	            Challenges: Challenges of policy {policy_title}"
        print(prompt)
        response = response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    def load_dashboard_prompt(self,policies:list,current_user:list) -> list:
        prompt = f"""From this using the user's info as given :- {current_user[0]}, {current_user[1]} {current_user[2]}, {current_user[3]} just suggest me the indices from this policy list that I can display to this user :- {policies}. Dont return anything else only return a single line with indices thats all"""
        res = response = response = self.client.models.generate_content(
              model="gemini-2.5-flash",
              contents=prompt
        )
        res = res.text
        print(res)
        policy_indices = process_indices(res)
        pol = []
        for i in policy_indices:
            pol.append(policies[i])
        return pol