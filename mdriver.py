from user_agents import parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random, time, os

import undetected_chromedriver as uc

def make_user_agent(ua, is_mobile):
    user_agent = parse(ua)
    model = user_agent.device.model
    platform = user_agent.os.family
    platform_version = user_agent.os.version_string + ".0.0"
    version = user_agent.browser.version[0]
    ua_full_version = user_agent.browser.version_string
    architecture = "x86"
    print(platform)
    if is_mobile:
        platform_info = "Linux armv8l"
        architecture= ""
    else: # Window
        platform_info = "Win32"
        model = ""
    RET_USER_AGENT = {
        "appVersion" : ua.replace("Mozilla/", ""),
        "userAgent": ua,
        "platform" : f"{platform_info}",
        "acceptLanguage" : "ko-KR, kr, en-US, en",
        "userAgentMetadata":{
            "brands" : [
                {"brand":"Not A(Brand", "version":"99"},
                {"brand":"Google Chrome", "version":f"{version}"},
                {"brand":"Chromium", "version":f"{version}"},
            ],
            "fullVersionList":[     # navigator.userAgentData.getHighEntropyValues(["fullVersionList"]).then(ua => {console.log(ua);}); 로 확인
                {"brand":"Not A(Brand", "version":"99"},
                {"brand":"Google Chrome", "version":f"{version}"},
                {"brand":"Chromium", "version":f"{version}"},
            ],
            "fullVersion":f"{ua_full_version}",
            "platform" :platform,
            "platformVersion":platform_version,
            "architecture":architecture,
            "model" : model,
            "mobile":is_mobile #True, False
        }
    }
    return RET_USER_AGENT

def read_agents():
    agents = []
    f = open("./useragents.txt","r",encoding="utf8")
    while True:
        line = f.readline()
        if not line:
            break
        agents.append(line.rstrip())
    return agents

def make_driver(account_id):
    try:
        pc_device = ["1920,1440","1920,1200","1920,1080","1600,1200","1600,900",
                        "1536,864", "1440,1080","1440,900","1360,768"
                ]

        mo_device = [
                    "360,640", "360,740", "375,667", "375,812", "412,732", "412,846",
                    "412,869", "412,892", "412,915"
                ]

        width,height = random.choice(mo_device).split(",")
 

        UA_list = read_agents()
        UA = random.choice(UA_list)  #seed = time.time()
     
        options = uc.ChromeOptions()

        #폴더가 없다면, 생성
        folder = os.path.join('C:\\',"cookies")
        if not os.path.exists(folder):
            os.makedirs(folder)
        cookie_folder_name = os.path.join(folder, account_id)
        if not os.path.exists(cookie_folder_name):
            os.makedirs(cookie_folder_name)

        #작업별 쿠키 기록을 남김
        # options.user_data_dir = cookie_folder_name

        # User Agent 속이기
        options.add_argument(f'--user-agent={UA}')
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
        options.add_argument('--disable-logging')
        
        driver = uc.Chrome(user_data_dir=cookie_folder_name,options=options)

        UA_Data = make_user_agent(UA,True)
        driver.execute_cdp_cmd("Network.setUserAgentOverride",UA_Data)

        # Max Touch Point 변경
        Mobile = {"enabled":True, "maxTouchPoints": random.choice([1,5])}
        driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled",Mobile)
        driver.execute_cdp_cmd("Emulation.setNavigatorOverrides",{"platform":"Linux armv8l"})
        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride",{
            "width":int(width),
            "height":int(height),
            "deviceScaleFactor":1,
            "mobile" : True
        })

        # 위치 정보 변경 Geo Location 변경하기
        def generate_random_geolocation():
            ltop_lat = 37.75415601640249
            ltop_long = 126.86767642302573
            rbottom_lat = 37.593829172663945
            rbottom_long = 127.15276051439332

            targetLat = random.uniform(rbottom_lat, ltop_lat)
            targetLong = random.uniform(ltop_long,rbottom_long)
            return {"latitude":targetLat, "longitude" : targetLong, "accuracy":100}
        GEO_DATA = generate_random_geolocation()
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", GEO_DATA)

        # User Agent 적용
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride",UA_Data)
        print(width,height)
        driver.set_window_size(int(width),int(height))
        
        return driver
    except Exception as e:
        print(f'드라이버 만드는 중 오류 발생 : {e}')
        driver = None
        return driver