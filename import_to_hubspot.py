import pandas as pd
import requests
import time

data = pd.read_excel('data.xlsx')
df = pd.DataFrame(data)
print(df)


# Your private app token from HubSpot
HUBSPOT_API_KEY = "pat-na1-fe37daad-9fb0-423d-8ced-c4e0f0666c14"

headers = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

# # Loop through rows and create contacts
for index, row in data.iterrows():
    full_name = row['name'].split()
    firstname = full_name[0]
    lastname = " ".join(full_name[1:]) if len(full_name) > 1 else ""
    
    contact_data = {
        "properties": {
            "firstname": firstname,
            "lastname": lastname,
            "email": row['email'],
            "phone": str(row['phone'])
        }
    }

    response = requests.post(
        "https://api.hubapi.com/crm/v3/objects/contacts",
        headers=headers,
        json=contact_data
    )

    if response.status_code == 201:
        print(f"Contact created for {row['name']}")
    else:
        print(f"Failed to create contact for {row['name']}")
        print(response.status_code, response.text)


# Base URL
BASE_URL = "https://api.hubapi.com"

for index, row in data.iterrows():
    email = row['email']
    
    search_url = f"{BASE_URL}/crm/v3/objects/contacts/search"
    search_body = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }]
    }

    search_resp = requests.post(search_url, headers=headers, json=search_body)
    if search_resp.status_code != 200:
        print(f"Failed to find contact for {email}")
        continue
    
    results = search_resp.json().get("results", [])
    if not results:
        print(f"No contact found for {email}")
        continue
    
    contact_id = results[0]["id"]

    # 2. Create a deal
    deal_data = {
        "properties": {
            "dealname": row['deal_name'],
            "amount": row['deal_value'],
            "dealstage": "appointmentscheduled",  # or "qualifiedtobuy" etc. (customize as needed)
            "pipeline": "default"
        }
    }

    deal_resp = requests.post(f"{BASE_URL}/crm/v3/objects/deals", headers=headers, json=deal_data)
    if deal_resp.status_code != 201:
        print(f"Failed to create deal for {row['deal_name']}")
        continue

    deal_id = deal_resp.json()["id"]

   # 3. Associate deal with contact
    assoc_url = f"{BASE_URL}/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/3"
    assoc_resp = requests.put(assoc_url, headers=headers)

    # Log the entire response for debugging
    if assoc_resp.status_code == 200:
        print(f"Deal '{row['deal_name']}' created and associated with {row['name']}")
    else:
        print(f"Failed to associate deal '{row['deal_name']}' with {row['name']}. "
            f"Status Code: {assoc_resp.status_code}, Reason: {assoc_resp.text}")