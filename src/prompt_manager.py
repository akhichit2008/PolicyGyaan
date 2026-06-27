from google import genai


class PromptManager:
    def __init__(self,client,model="gemini-2.5-flash"):
        self.client = client
        self.model = model

    def policy_redirect_prompt(self,policy_title,current_user):
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