from playwright.sync_api import sync_playwright
import os, time, random


def human_delay(min_ms=200, max_ms=700):
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


def generate_campaign_names(count=1):
    base_timestamp = int(time.time())
    return [f"Campaign_{base_timestamp + (i * 60)}_{i+1}" for i in range(count)]


def select_agent(page, agent_value):
    if agent_value.lower() == "chatgpt":
        print("🤖 Selecting ChatGPT Agent...")

        for possible in ["chatgpt", "gpt", "ai", "openai"]:
            try:
                page.select_option("#Agents", value=possible)
                print(f"✓ Selected ChatGPT by value='{possible}'")
                return
            except:
                pass

        options = page.locator("#Agents option")
        for i in range(options.count()):
            text = options.nth(i).inner_text().lower()
            val = options.nth(i).get_attribute("value")
            if any(x in text for x in ["chatgpt", "gpt", "ai"]):
                page.select_option("#Agents", value=val)
                print(f"✓ Selected ChatGPT by text → value='{val}'")
                return

        print("⚠ ChatGPT agent NOT FOUND!")
        return

    print(f"👤 Selecting Agent '{agent_value}'")
    page.select_option("#Agents", value=agent_value)


def go_to_create_campaign(page, campaign_name, org_name, agent_value, excel_path):
    print(f"🚀 Creating campaign: {campaign_name}")

    # page.goto("https://fe.callbotics.ai/content/create_campaign")
    page.click("h6.sidebar-menu-item:text('Create Campaign')")
    page.wait_for_load_state("networkidle")

    page.locator("#campaignName").type(campaign_name)
    human_delay()

    page.select_option("#organisationName", value=org_name)
    page.select_option("#processType", value="OTHER")
    page.select_option("#qa_parameters_list", value="None")

    page.locator("#background_noise").type("alpha")
    page.locator("#background_noise_volume").type("02")

    human_delay()
    page.locator("#step1btn").click()
    page.wait_for_load_state("networkidle")

    print(f"📂 Uploading Excel: {excel_path}")
    page.set_input_files("#formFile3", excel_path)

    page.wait_for_selector("button.swal2-confirm")
    page.locator("button.swal2-confirm").click()
    page.wait_for_selector(".swal2-popup", state="detached")

    page.locator("#step2btn").click()
    select_agent(page, agent_value)

    page.locator("#step3btn").click()
    page.wait_for_selector("button.swal2-confirm")
    page.locator("button.swal2-confirm").click()

    page.locator("#step4btn").click()
    page.wait_for_selector("button.swal2-confirm")
    page.locator("button.swal2-confirm").click()

    print(f"✅ Campaign '{campaign_name}' created!\n")


def run_campaign_creator(org_name, agent_value, excel_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # ALWAYS LOGIN FRESH
        print("🔐 Logging in fresh...")
        page.goto("https://fe.callbotics.ai/login_home")
        page.wait_for_load_state("networkidle")

        page.locator('[name="username"]').type("admin")
        human_delay()
        page.locator('[name="password"]').type("Hls0f12CIsV8")
        human_delay()

        page.locator('[type="submit"]').click()
        page.wait_for_load_state("networkidle")

        print("🔓 Login successful!\n")

        campaigns = generate_campaign_names(1)

        for name in campaigns:
            go_to_create_campaign(page, name, org_name, agent_value, excel_path)

            page.goto("https://fe.callbotics.ai/dashboard")
            # print("⏳ Waiting 60 seconds...\n")
            # time.sleep(60)

        print("🎉 All campaigns created!")
        browser.close()

if __name__ == "__main__":
    run_campaign_creator(
        org_name="Callbotics_Org",
        agent_value="chatgpt",
        excel_path="/home/test/Desktop/call/contact.xlsx"
    )
