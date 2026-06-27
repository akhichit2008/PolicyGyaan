import re
import json


def process_indices(indices):
    indices_new = []
    print(indices.split())
    for indice in indices.split():
        if "," in indice:
            indices_new.append(int(indice.strip()[:len(indice)-1]))
        else:
            indices_new.append(int(indice.strip()))
    return indices_new


def load_default_policy():
    policies = []
    with open("datastore.json","r") as f:
        data = json.load(f)
    for policy in data["policies"]:
        policies.append(policy)
    print(policies)
    return policies

def allowed_file(filename):
	ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def policy_filter(res):
    # Pattern-Oriented Filtering to Avoid unwanted symbols in LLM API outputs
    policy_overview = re.search(r"(?i)\*\*.*?Overview.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)

    impact_on_you = re.search(r"(?i)\*\*.*?Impact.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)

    history = re.search(r"(?i)\*\*.*?History.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)

    key_benefits = re.search(r"(?i)\*\*.*?Benefits.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)

    challenges = re.search(r"(?i)\*\*.*?Challenges.*?\*\*\s*(.*)", res, re.DOTALL) # Last section

    policy_overview = policy_overview.group(1).strip() if policy_overview else "Not available"

    impact_on_you = impact_on_you.group(1).strip() if impact_on_you else "Not available"

    history = history.group(1).strip() if history else "Not available"

    key_benefits = key_benefits.group(1).strip() if key_benefits else "Not available"

    challenges = challenges.group(1).strip() if challenges else "Not available"

    return (policy_overview,impact_on_you,history,key_benefits,challenges)