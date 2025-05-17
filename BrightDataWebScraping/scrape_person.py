import requests
import json
#get a new login and run (trogger data alr prepared)

# print("Triggering LinkedIn scraping...")

# trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
# trigger_headers = {
#     "Authorization": "Bearer f21b2e641d638526a171e025e13c63fadd9de92112b49b810d64e0782a08260b",
#     "Content-Type": "application/json",
# }
# trigger_params = {
#     "dataset_id": "gd_l1viktl72bvl7bjuj0",
#     "include_errors": "true",
# }

# trigger_data =[]

# with open('./trigger_data_copy.txt','r') as f:
#     trigger_data = json.load(f)

# trigger_response = requests.post(trigger_url, headers=trigger_headers, params=trigger_params, json=trigger_data)

# if trigger_response.status_code == 200:
#     print("Scraping triggered successfully!")
# else:
#     print(f"Trigger failed: {trigger_response.status_code}, {trigger_response.text}")
#     exit()

# snapshot_id = (trigger_response.json())
# print(snapshot_id)

# --------

print(" Downloading scraped data...")

snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/s_mad98mgf13dcokpy3l"
snapshot_headers = {
    "Authorization": "Bearer f21b2e641d638526a171e025e13c63fadd9de92112b49b810d64e0782a08260b",
}
snapshot_params = {
    "format": "json",
}

snapshot_response = requests.get(snapshot_url, headers=snapshot_headers, params=snapshot_params)

if snapshot_response.status_code == 200:
    data = snapshot_response.json()
    print(f" Downloaded {len(data)} profiles.")
else:
    print(f" Download failed: {snapshot_response.status_code}, {snapshot_response.text}")
    exit()

# 4. Save JSON to File
print("💾 Saving data to JSON file...")

with open('linkedin_profiles_raw_15.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("🎉 All done! Your data is saved to linkedin_profiles_raw_15.json")



# ## s_mad9a3ej1xm65s49wh - insufficient
