import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import tomlkit  # 使用 tomlkit 来处理带注释的 TOML 文件
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import requests
import re
import json
###################################################################################################################
#\

###################################################################################################################
#配置文件读取与写入
config_path = "config.toml"  # 配置文件路径

def load_config():
    global config_data, favorite_paths, collection_list
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = tomlkit.parse(file.read())
        update_ui_from_config()
        favorite_paths = config_data.get("favorite_list", {})
        collection_list = config_data.get("collection_list", {})
        update_favorite_dropdown()
        update_collection_dropdown()
        messagebox.showinfo("Success", "配置加载成功.")
    except Exception as e:
        messagebox.showerror("Error", f"配置加载失败: {e}")

def import_config():
    """导入其他位置的配置文件"""
    global config_path
    path = filedialog.askopenfilename(filetypes=[("TOML files", "*.toml"), ("All files", "*.*")])
    if path:
        config_path = path
        load_config()
        
def save_config():
    """保存配置到文件，保留注释"""
    try:
        # 更新基础设置
        config_data["video_name"] = "{{" + video_name_var.get() + "}}"
        config_data["page_name"] = "{{" + page_name_var.get() + "}}"
        config_data["interval"] = int(interval_var.get())
        config_data["upper_path"] = upper_path_var.get()
        config_data["nfo_time_type"] = nfo_time_type_var.get()

        # 更新凭证设置
        config_data["credential"]["sessdata"] = sessdata_var.get()
        config_data["credential"]["bili_jct"] = bili_jct_var.get()
        config_data["credential"]["buvid3"] = buvid3_var.get()
        config_data["credential"]["dedeuserid"] = dedeuserid_var.get()
        config_data["credential"]["ac_time_value"] = ac_time_value_var.get()

        # 更新过滤选项
        config_data["filter_option"]["video_max_quality"] = video_max_quality_var.get()
        config_data["filter_option"]["video_min_quality"] = video_min_quality_var.get()
        config_data["filter_option"]["audio_max_quality"] = audio_max_quality_var.get()
        config_data["filter_option"]["audio_min_quality"] = audio_min_quality_var.get()
        config_data["filter_option"]["codecs"] = list(codecs_list.get(0, tk.END))  # 获取所有listbox中的项
        config_data["filter_option"]["no_dolby_video"] = no_dolby_video_var.get()
        config_data["filter_option"]["no_dolby_audio"] = no_dolby_audio_var.get()
        config_data["filter_option"]["no_hdr"] = no_hdr_var.get()
        config_data["filter_option"]["no_hires"] = no_hires_var.get()

        # 更新弹幕设置
        config_data["danmaku_option"]["duration"] = duration_var.get()
        config_data["danmaku_option"]["font"] = font_var.get()
        config_data["danmaku_option"]["font_size"] = font_size_var.get()
        config_data["danmaku_option"]["width_ratio"] = width_ratio_var.get()
        config_data["danmaku_option"]["horizontal_gap"] = horizontal_gap_var.get()
        config_data["danmaku_option"]["lane_size"] = lane_size_var.get()
        config_data["danmaku_option"]["float_percentage"] = float_percentage_var.get()
        config_data["danmaku_option"]["bottom_percentage"] = bottom_percentage_var.get()
        config_data["danmaku_option"]["opacity"] = opacity_var.get()
        config_data["danmaku_option"]["bold"] = bold_var.get()
        config_data["danmaku_option"]["outline"] = outline_var.get()
        config_data["danmaku_option"]["time_offset"] = time_offset_var.get()

        # 更新收藏夹设置
        config_data["favorite_list"] = favorite_paths

        # 更新合集列表设置
        config_data["collection_list"] = collection_list
        
        with open(config_path, "w", encoding='utf-8') as file:
            file.write(tomlkit.dumps(config_data))
        messagebox.showinfo("Success", "配置保存成功.")
        update_info_bar("配置已保存")
    except Exception as e:
        messagebox.showerror("Error", f"配置保存失败: {e}")
        update_info_bar(f"错误: {e}")

###################################################################################################################
#配置数据更新
def update_ui_from_config():
    """将加载的配置更新到UI组件，处理带有{{}}的字段"""
    # 更新基础设置
    video_name_var.set(config_data["video_name"].strip("{}"))
    page_name_var.set(config_data["page_name"].strip("{}"))
    interval_var.set(str(config_data["interval"]))
    upper_path_var.set(config_data["upper_path"])
    nfo_time_type_var.set(config_data["nfo_time_type"])

    # 更新凭据设置
    sessdata_var.set(config_data["credential"]["sessdata"])
    bili_jct_var.set(config_data["credential"]["bili_jct"])
    buvid3_var.set(config_data["credential"]["buvid3"])
    dedeuserid_var.set(config_data["credential"]["dedeuserid"])
    ac_time_value_var.set(config_data["credential"]["ac_time_value"])

    # 更新画质音质设置
    video_max_quality_var.set(config_data["filter_option"]["video_max_quality"])
    video_min_quality_var.set(config_data["filter_option"]["video_min_quality"])
    audio_max_quality_var.set(config_data["filter_option"]["audio_max_quality"])
    audio_min_quality_var.set(config_data["filter_option"]["audio_min_quality"])
    codecs_list.delete(0, tk.END)
    for codec in config_data["filter_option"]["codecs"]:
        codecs_list.insert(tk.END, codec)
    no_dolby_video_var.set(config_data["filter_option"]["no_dolby_video"])
    no_dolby_audio_var.set(config_data["filter_option"]["no_dolby_audio"])
    no_hdr_var.set(config_data["filter_option"]["no_hdr"])
    no_hires_var.set(config_data["filter_option"]["no_hires"])

    # 更新弹幕设置
    duration_var.set(config_data["danmaku_option"]["duration"])
    font_var.set(config_data["danmaku_option"]["font"])
    font_size_var.set(config_data["danmaku_option"]["font_size"])
    width_ratio_var.set(config_data["danmaku_option"]["width_ratio"])
    horizontal_gap_var.set(config_data["danmaku_option"]["horizontal_gap"])
    lane_size_var.set(config_data["danmaku_option"]["lane_size"])
    float_percentage_var.set(config_data["danmaku_option"]["float_percentage"])
    bottom_percentage_var.set(config_data["danmaku_option"]["bottom_percentage"])
    opacity_var.set(config_data["danmaku_option"]["opacity"])
    bold_var.set(config_data["danmaku_option"]["bold"])
    outline_var.set(config_data["danmaku_option"]["outline"])
    time_offset_var.set(config_data["danmaku_option"]["time_offset"])

    update_info_bar("配置已加载")

def update_info_bar(message):
    info_bar.config(state=tk.NORMAL)
    info_bar.insert(tk.END, message + '\n')
    info_bar.see(tk.END)
    info_bar.config(state=tk.DISABLED)

def browse_folder(entry_field):
    # 打开文件夹选择对话框，并获取选择的文件夹路径
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, folder_selected)
        
# 更新凭据模块-联网-Edge
def get_cookies_and_local_storage_from_edge(login_url, main_url):
    """从 Edge 浏览器获取 Bilibili 的 cookies 和 local storage"""
    # 设置Edge浏览器的选项
    edge_options = Options()
    edge_options.add_argument('inprivate')  # 启用匿名模式
    # edge_options.add_argument('--headless')  # 无头模式，可选，但在此场景下不建议使用

    # 启动Edge浏览器
    with webdriver.Edge(options=edge_options) as driver:
        driver.get(login_url)

        # 等待用户手动完成登录操作
        print("请在浏览器中手动完成登录操作...")
        WebDriverWait(driver, timeout=600).until(
            lambda d: d.current_url.startswith(main_url)
        )

        # 获取Cookies
        cookies = driver.get_cookies()
        credentials = print_bilibili_credentials(cookies)

        # 获取Local Storage中的值
        ac_time_value = driver.execute_script("return window.localStorage.getItem('ac_time_value');")
        credentials['ac_time_value'] = ac_time_value

        # 更新UI
        sessdata_var.set(credentials['sessdata'])
        bili_jct_var.set(credentials['bili_jct'])
        buvid3_var.set(credentials['buvid3'])
        dedeuserid_var.set(credentials['dedeuserid'])
        ac_time_value_var.set(credentials['ac_time_value'])

def print_bilibili_credentials(cookies):
    """打印并返回Bilibili的登录后凭证"""
    credentials_dict = {'sessdata': '', 'bili_jct': '', 'buvid3': '', 'buvid4': '', 'dedeuserid': ''}
    for cookie in cookies:
        if cookie['name'].lower() in credentials_dict:
            credentials_dict[cookie['name'].lower()] = cookie['value']
    return credentials_dict

def update_credentials():
    """更新凭证的线程函数"""
    login_url = 'https://passport.bilibili.com/login'
    main_url = 'https://www.bilibili.com/'
    get_cookies_and_local_storage_from_edge(login_url, main_url)

def start_update_credentials_thread():
    thread = threading.Thread(target=update_credentials)
    thread.start()
    update_info_bar("调用Edge浏览器匿名模式更新凭据，推荐扫码登录")

# 更新收藏夹模块
def update_favorite_dropdown():
    """更新下拉列表中的选项"""
    favorite_id_dropdown['menu'].delete(0, 'end')
    for k in favorite_paths.keys():
        favorite_id_dropdown['menu'].add_command(label=k, command=tk._setit(favorite_id_var, k))
    if favorite_paths:
        favorite_id_var.set(next(iter(favorite_paths)))
        update_favorites_display(None)
    else:
        favorite_id_var.set('')
        path_entry.delete(0, tk.END)

def update_favorites_display(*args):
    """更新输入框显示对应的路径"""
    selected_id = favorite_id_var.get()
    path_entry.delete(0, tk.END)
    if selected_id in favorite_paths:
        path_entry.insert(0, favorite_paths[selected_id])

def add_favorite():
    """添加新的收藏夹配置"""
    id = new_id_entry.get()
    path = new_path_entry.get()
    if id and path:
        favorite_paths[id] = path
        update_favorite_dropdown()
        save_config()
        update_info_bar(f"添加新的收藏夹: ID={id}, 路径={path}")
    else:
        messagebox.showerror("Error", "ID和路径不能为空")

def update_favorite():
    """更新现有的收藏夹配置"""
    id = favorite_id_var.get()
    path = path_entry.get()
    if id in favorite_paths:
        favorite_paths[id] = path
        save_config()
        update_info_bar(f"更新收藏夹信息: ID={id}, 新的路径={path}")
    else:
        messagebox.showerror("Error", "请选择有效的收藏夹ID")

def delete_favorite():
    """删除选定的收藏夹配置"""
    id = favorite_id_var.get()
    if id in favorite_paths:
        del favorite_paths[id]
        update_favorite_dropdown()
        save_config()
        update_info_bar(f"删除选定的收藏夹: ID={id}")
    else:
        messagebox.showerror("Error", "请选择有效的收藏夹ID")

# 更新合集模块
def update_collection_dropdown():
    collection_id_dropdown['menu'].delete(0, 'end')
    type = type_var.get()
    for k in collection_list.keys():
        if k.startswith(type + ':'):
            collection_id_dropdown['menu'].add_command(label=k, command=tk._setit(collection_id_var, k))
    if collection_list:
        first_key = next((k for k in collection_list if k.startswith(type + ':')), '')
        collection_id_var.set(first_key)
        update_collections_display(None)
    else:
        collection_id_var.set('')
        path_entry_collection.delete(0, tk.END)

def update_collections_display(*args):
    selected_id = collection_id_var.get()
    path_entry_collection.delete(0, tk.END)
    if selected_id in collection_list:
        path_entry_collection.insert(0, collection_list[selected_id])

def add_collection():
    category = type_var.get()
    mid = mid_entry.get()
    season_or_series_id = id_entry.get()
    path = new_path_entry_collection.get()

    if not (category and mid and season_or_series_id and path):
        messagebox.showerror("错误", "类型、mid、series_id/season_id 和路径都不能为空")
        return

    key = f"{category}:{mid}:{season_or_series_id}"
    if key in collection_list:
        messagebox.showwarning("警告", "该项目已经存在!")
        return

    collection_list[key] = path
    update_collection_dropdown()
    save_config()
    update_info_bar(f"添加一个新合集: Key={key}, 路径={path}")

def type_changed(*args):
    update_collection_dropdown()

def update_collection():
    id = collection_id_var.get()
    path = path_entry_collection.get()
    if id in collection_list:
        collection_list[id] = path
        save_config()
        update_info_bar(f"更新合集信息: ID={id}, New Path={path}")
    else:
        messagebox.showerror("Error", "请选择有效的合集ID")

def delete_collection():
    id = collection_id_var.get()
    if id in collection_list:
        del collection_list[id]
        update_collection_dropdown()
        save_config()
        update_info_bar(f"删除合集: ID={id}")
    else:
        messagebox.showerror("Error", "请选择有效的合集ID")

# 添加用户合集-api-bilibili用户主页链接
def extract_user_id(homepage_url):
    match = re.search(r'space\.bilibili\.com/(\d+)', homepage_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("无法从主页链接中提取用户ID")

def fetch_and_display_collections():
    homepage_url = simpledialog.askstring("输入", "请输入Bilibili用户主页链接（网页版主页）:")
    if not homepage_url:
        return

    try:
        user_id = extract_user_id(homepage_url)
        items_lists = get_user_collections_and_playlists(user_id)
        if items_lists:
            display_results(items_lists)
            update_info_bar(f"Fetched collections and playlists for user ID={user_id}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        update_info_bar(f"Failed to fetch collections and playlists: {str(e)}")

def get_user_collections_and_playlists(user_id):
    url = f"https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={user_id}&page_num=1&page_size=20"
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    if data['code'] != 0:
        raise Exception("Failed to fetch data from Bilibili API.")

    items_lists = []
    for category in ['seasons_list', 'series_list']:
        if category in data['data']['items_lists']:
            for item in data['data']['items_lists'][category]:
                meta = item['meta']
                category_name = "season" if meta['category'] == 0 else "series"
                season_or_series_id = meta.get('season_id', meta.get('series_id', 'N/A'))
                formatted_output = f"{category_name}|{meta['name']}|{meta['description']}|{meta['mid']}|{season_or_series_id}|{meta['total']}"
                items_lists.append(formatted_output)
    return items_lists

def display_results(items_lists):
    new_window = tk.Toplevel(root)
    new_window.title("选择要添加的项目")
    listbox = tk.Listbox(new_window, width=100, height=10)
    listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    for item in items_lists:
        listbox.insert(tk.END, item)

    def add_selected_to_config():
        selected = listbox.get(listbox.curselection())
        category, name, description, mid, season_or_series_id, total_videos = selected.split('|')
        type_var.set(category)
        mid_entry.delete(0, tk.END)
        mid_entry.insert(0, mid)
        id_entry.delete(0, tk.END)
        id_entry.insert(0, season_or_series_id)
        new_path_entry_collection.delete(0, tk.END)
        new_path_entry_collection.insert(0, f"./{name}/")
        new_window.destroy()

    select_button = ttk.Button(new_window, text="添加选中项目", command=add_selected_to_config)
    select_button.pack(pady=10)

###################################################################################################################
# 页面设置   
root = tk.Tk()
root.title("配置文件编辑器")

tab_control = ttk.Notebook(root)

tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="基本设置")

tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="凭证设置")

tab3 = ttk.Frame(tab_control)
tab_control.add(tab3, text="过滤选项")

tab4 = ttk.Frame(tab_control)
tab_control.add(tab4, text="弹幕设置")

tab5 = ttk.Frame(tab_control)
tab_control.add(tab5, text="收藏夹管理")

tab6 = ttk.Frame(tab_control)
tab_control.add(tab6, text="合集管理")

tab_control.pack(expand=1, fill="both")

# 信息栏
info_bar = tk.Text(root, height=10, state=tk.DISABLED)
info_bar.pack(side=tk.BOTTOM, fill=tk.X)

###################################################################################################################
# 创建基础设置控件并放置
video_name_var = tk.StringVar()
video_name_options = ["title", "bvid", "upper_name", "upper_mid"]
video_name_label = ttk.Label(tab1, text="视频名称 (Video Name):")
video_name_label.grid(column=0, row=0, padx=10, pady=10, sticky='w')
video_name_dropdown = ttk.OptionMenu(tab1, video_name_var, "", *video_name_options)
video_name_dropdown.grid(column=1, row=0)

page_name_var = tk.StringVar()
page_name_options = ["bvid", "ptitle", "pid"]
page_name_label = ttk.Label(tab1, text="页面名称 (Page Name):")
page_name_label.grid(column=0, row=1, padx=10, pady=10, sticky='w')
page_name_dropdown = ttk.OptionMenu(tab1, page_name_var, "", *page_name_options)
page_name_dropdown.grid(column=1, row=1)

interval_var = tk.StringVar()
interval_label = ttk.Label(tab1, text="间隔时间 (Interval, sec):")
interval_label.grid(column=0, row=2, padx=10, pady=10, sticky='w')
interval_entry = ttk.Entry(tab1, textvariable=interval_var)
interval_entry.grid(column=1, row=2)

upper_path_var = tk.StringVar()
upper_path_label = ttk.Label(tab1, text="上层路径 (Upper Path):")
upper_path_label.grid(column=0, row=3, padx=10, pady=10, sticky='w')
upper_path_entry = ttk.Entry(tab1, textvariable=upper_path_var)
upper_path_entry.grid(column=1, row=3)
upper_path_button = ttk.Button(tab1, text="浏览", command=lambda: browse_folder(upper_path_entry))
upper_path_button.grid(column=2, row=3)

nfo_time_type_var = tk.StringVar()
nfo_time_type_options = ["favtime", "pubtime"]
nfo_time_type_label = ttk.Label(tab1, text="信息时间类型 (NFO Time Type):")
nfo_time_type_label.grid(column=0, row=4, padx=10, pady=10, sticky='w')
nfo_time_type_dropdown = ttk.OptionMenu(tab1, nfo_time_type_var, "", *nfo_time_type_options)
nfo_time_type_dropdown.grid(column=1, row=4)

# 凭证输入框
sessdata_var = tk.StringVar()
sessdata_label = ttk.Label(tab2, text="sessdata:")
sessdata_label.grid(column=0, row=0, padx=10, pady=10, sticky='w')
sessdata_entry = ttk.Entry(tab2, textvariable=sessdata_var, width=50)
sessdata_entry.grid(column=1, row=0)

bili_jct_var = tk.StringVar()
bili_jct_label = ttk.Label(tab2, text="bili_jct:")
bili_jct_label.grid(column=0, row=1, padx=10, pady=10, sticky='w')
bili_jct_entry = ttk.Entry(tab2, textvariable=bili_jct_var, width=50)
bili_jct_entry.grid(column=1, row=1)

buvid3_var = tk.StringVar()
buvid3_label = ttk.Label(tab2, text="buvid3:")
buvid3_label.grid(column=0, row=2, padx=10, pady=10, sticky='w')
buvid3_entry = ttk.Entry(tab2, textvariable=buvid3_var, width=50)
buvid3_entry.grid(column=1, row=2)

dedeuserid_var = tk.StringVar()
dedeuserid_label = ttk.Label(tab2, text="dedeuserid:")
dedeuserid_label.grid(column=0, row=3, padx=10, pady=10, sticky='w')
dedeuserid_entry = ttk.Entry(tab2, textvariable=dedeuserid_var, width=50)
dedeuserid_entry.grid(column=1, row=3)

ac_time_value_var = tk.StringVar()
ac_time_value_label = ttk.Label(tab2, text="ac_time_value:")
ac_time_value_label.grid(column=0, row=4, padx=10, pady=10, sticky='w')
ac_time_value_entry = ttk.Entry(tab2, textvariable=ac_time_value_var, width=50)
ac_time_value_entry.grid(column=1, row=4)

# 添加更新凭证按钮
update_credentials_button = ttk.Button(tab2, text="更新凭证", command=start_update_credentials_thread)
update_credentials_button.grid(column=0, row=5, columnspan=2, padx=10, pady=10, sticky='w')

# 过滤设置，设置音视频质量
video_max_quality_var = tk.StringVar()
video_max_quality_label = ttk.Label(tab3, text="视频最高质量:")
video_max_quality_label.grid(column=0, row=0, padx=10, pady=10, sticky='w')
video_max_quality_dropdown = ttk.OptionMenu(tab3, video_max_quality_var, "", "Quality8k", "Quality4k", "Quality1080p60", "Quality1080pPLUS", "Quality1080p", "Quality720p", "Quality480p", "Quality360p")
video_max_quality_dropdown.grid(column=1, row=0)

video_min_quality_var = tk.StringVar()
video_min_quality_label = ttk.Label(tab3, text="视频最低质量:")
video_min_quality_label.grid(column=0, row=1, padx=10, pady=10, sticky='w')
video_min_quality_dropdown = ttk.OptionMenu(tab3, video_min_quality_var, "", "Quality8k", "Quality4k", "Quality1080p60", "Quality1080pPLUS", "Quality1080p", "Quality720p", "Quality480p", "Quality360p")
video_min_quality_dropdown.grid(column=1, row=1)

audio_max_quality_var = tk.StringVar()
audio_max_quality_label = ttk.Label(tab3, text="音频最高质量:")
audio_max_quality_label.grid(column=0, row=2, padx=10, pady=10, sticky='w')
audio_max_quality_dropdown = ttk.OptionMenu(tab3, audio_max_quality_var, "", "QualityHiRES", "Quality192k", "QualityDolby", "Quality132k", "Quality64k")
audio_max_quality_dropdown.grid(column=1, row=2)

audio_min_quality_var = tk.StringVar()
audio_min_quality_label = ttk.Label(tab3, text="音频最低质量:")
audio_min_quality_label.grid(column=0, row=3, padx=10, pady=10, sticky='w')
audio_min_quality_dropdown = ttk.OptionMenu(tab3, audio_min_quality_var, "", "QualityHiRES", "Quality192k", "QualityDolby", "Quality132k", "Quality64k")
audio_min_quality_dropdown.grid(column=1, row=3)

codecs_label = ttk.Label(tab3, text="编解码器顺序:")
codecs_label.grid(column=0, row=4, padx=10, pady=10, sticky='w')
codecs_list = tk.Listbox(tab3, height=5)
codecs_list.grid(column=1, row=4, padx=10, pady=10, sticky='w')

no_dolby_video_var = tk.BooleanVar()
no_dolby_video_check = ttk.Checkbutton(tab3, text="禁用杜比视频", variable=no_dolby_video_var)
no_dolby_video_check.grid(column=0, row=5, padx=10, pady=10, sticky='w')

no_dolby_audio_var = tk.BooleanVar()
no_dolby_audio_check = ttk.Checkbutton(tab3, text="禁用杜比音频", variable=no_dolby_audio_var)
no_dolby_audio_check.grid(column=1, row=5, padx=10, pady=10, sticky='w')

no_hdr_var = tk.BooleanVar()
no_hdr_check = ttk.Checkbutton(tab3, text="禁用HDR", variable=no_hdr_var)
no_hdr_check.grid(column=0, row=6, padx=10, pady=10, sticky='w')

no_hires_var = tk.BooleanVar()
no_hires_check = ttk.Checkbutton(tab3, text="禁用高分辨率音频", variable=no_hires_var)
no_hires_check.grid(column=1, row=6, padx=10, pady=10, sticky='w')

# 弹幕设置
duration_var = tk.DoubleVar()
duration_label = ttk.Label(tab4, text="弹幕持续时间(duration)，单位秒:")
duration_label.grid(column=0, row=0, padx=10, pady=10, sticky='w')
duration_entry = ttk.Entry(tab4, textvariable=duration_var)
duration_entry.grid(column=1, row=0)

font_var = tk.StringVar()
font_label = ttk.Label(tab4, text="弹幕字体(font):")
font_label.grid(column=0, row=1, padx=10, pady=10, sticky='w')
font_entry = ttk.Entry(tab4, textvariable=font_var)
font_entry.grid(column=1, row=1)

font_size_var = tk.IntVar()
font_size_label = ttk.Label(tab4, text="弹幕的字体大小(font_size):")
font_size_label.grid(column=0, row=2, padx=10, pady=10, sticky='w')
font_size_entry = ttk.Entry(tab4, textvariable=font_size_var)
font_size_entry.grid(column=1, row=2)

width_ratio_var = tk.DoubleVar()
width_ratio_label = ttk.Label(tab4, text="弹幕宽度的比例(width_ratio):")
width_ratio_label.grid(column=0, row=3, padx=10, pady=10, sticky='w')
width_ratio_entry = ttk.Entry(tab4, textvariable=width_ratio_var)
width_ratio_entry.grid(column=1, row=3)

horizontal_gap_var = tk.DoubleVar()
horizontal_gap_label = ttk.Label(tab4, text="最小的水平距离(horizontal_gap):")
horizontal_gap_label.grid(column=0, row=4, padx=10, pady=10, sticky='w')
horizontal_gap_entry = ttk.Entry(tab4, textvariable=horizontal_gap_var)
horizontal_gap_entry.grid(column=1, row=4)

lane_size_var = tk.IntVar()
lane_size_label = ttk.Label(tab4, text="弹幕所占据的高度(lane_size):")
lane_size_label.grid(column=0, row=5, padx=10, pady=10, sticky='w')
lane_size_entry = ttk.Entry(tab4, textvariable=lane_size_var)
lane_size_entry.grid(column=1, row=5)

float_percentage_var = tk.DoubleVar()
float_percentage_label = ttk.Label(tab4, text="滚动弹幕最多高度百分比(float_percentage):")
float_percentage_label.grid(column=0, row=6, padx=10, pady=10, sticky='w')
float_percentage_entry = ttk.Entry(tab4, textvariable=float_percentage_var)
float_percentage_entry.grid(column=1, row=6)

bottom_percentage_var = tk.DoubleVar()
bottom_percentage_label = ttk.Label(tab4, text="底部弹幕最多高度百分比(bottom_percentage):")
bottom_percentage_label.grid(column=0, row=7, padx=10, pady=10, sticky='w')
bottom_percentage_entry = ttk.Entry(tab4, textvariable=bottom_percentage_var)
bottom_percentage_entry.grid(column=1, row=7)

opacity_var = tk.IntVar()
opacity_label = ttk.Label(tab4, text="透明度(opacity):")
opacity_label.grid(column=0, row=8, padx=10, pady=10, sticky='w')
opacity_entry = ttk.Entry(tab4, textvariable=opacity_var)
opacity_entry.grid(column=1, row=8)

bold_var = tk.BooleanVar()
bold_label = ttk.Label(tab4, text="是否加粗(bold):")
bold_label.grid(column=0, row=9, padx=10, pady=10, sticky='w')
bold_entry = ttk.Checkbutton(tab4, variable=bold_var)
bold_entry.grid(column=1, row=9)

outline_var = tk.DoubleVar()
outline_label = ttk.Label(tab4, text="描边宽度(outline):")
outline_label.grid(column=0, row=10, padx=10, pady=10, sticky='w')
outline_entry = ttk.Entry(tab4, textvariable=outline_var)
outline_entry.grid(column=1, row=10)

time_offset_var = tk.DoubleVar()
time_offset_label = ttk.Label(tab4, text="时间轴偏移(time_offset):")
time_offset_label.grid(column=0, row=11, padx=10, pady=10, sticky='w')
time_offset_entry = ttk.Entry(tab4, textvariable=time_offset_var)
time_offset_entry.grid(column=1, row=11)

# 收藏夹管理标签页
favorite_paths = {}

favorite_id_var = tk.StringVar()
favorite_id_label = ttk.Label(tab5, text="收藏夹ID:")
favorite_id_label.grid(column=0, row=0, padx=10, pady=10, sticky='w')
favorite_id_dropdown = ttk.OptionMenu(tab5, favorite_id_var, "")
favorite_id_dropdown.grid(column=1, row=0)
favorite_id_var.trace_add('write', update_favorites_display)

path_entry = ttk.Entry(tab5, width=50)
path_entry.grid(column=1, row=1, padx=10, pady=10, sticky='w')

add_button = ttk.Button(tab5, text="添加新收藏夹", command=add_favorite)
add_button.grid(column=0, row=2, padx=10, pady=10)

update_button = ttk.Button(tab5, text="更新收藏夹", command=update_favorite)
update_button.grid(column=1, row=2, padx=10, pady=10)

delete_button = ttk.Button(tab5, text="删除收藏夹", command=delete_favorite)
delete_button.grid(column=2, row=2, padx=10, pady=10)

new_id_label = ttk.Label(tab5, text="新收藏夹ID:")
new_id_label.grid(column=0, row=3, padx=10, pady=10, sticky='w')
new_id_entry = ttk.Entry(tab5, width=50)
new_id_entry.grid(column=1, row=3)

new_path_label = ttk.Label(tab5, text="新收藏夹路径:")
new_path_label.grid(column=0, row=4, padx=10, pady=10, sticky='w')
new_path_entry = ttk.Entry(tab5, width=50)
new_path_entry.grid(column=1, row=4)

# 合集管理标签页
collection_list = {}

type_var = tk.StringVar()
type_var.set("series")  # 设置默认值
type_label = ttk.Label(tab6, text="类型:")
type_label.grid(column=0, row=3, padx=10, pady=10, sticky='w')
type_dropdown = ttk.OptionMenu(tab6, type_var, "", "series", "season")
type_dropdown.grid(column=1, row=3)

type_var.trace_add('write', type_changed)

mid_label = ttk.Label(tab6, text="mid:")
mid_label.grid(column=0, row=4, padx=10, pady=10, sticky='w')
mid_entry = ttk.Entry(tab6, width=50)
mid_entry.grid(column=1, row=4)

id_label = ttk.Label(tab6, text="series_id/season_id:")
id_label.grid(column=0, row=6, padx=10, pady=10, sticky='w')
id_entry = ttk.Entry(tab6, width=50)
id_entry.grid(column=1, row=6)

collection_id_var = tk.StringVar()
collection_id_label = ttk.Label(tab6, text="合集ID:")
collection_id_label.grid(column=0, row=0, padx=10, pady=10, sticky='w')
collection_id_dropdown = ttk.OptionMenu(tab6, collection_id_var, "")
collection_id_dropdown.grid(column=1, row=0)
collection_id_var.trace_add('write', update_collections_display)

path_entry_collection = ttk.Entry(tab6, width=50)
path_entry_collection.grid(column=1, row=1, padx=10, pady=10, sticky='w')

add_button_collection = ttk.Button(tab6, text="添加新合集", command=add_collection)
add_button_collection.grid(column=0, row=2, padx=10, pady=10)

update_button_collection = ttk.Button(tab6, text="更新合集", command=update_collection)
update_button_collection.grid(column=1, row=2, padx=10, pady=10)

delete_button_collection = ttk.Button(tab6, text="删除合集", command=delete_collection)
delete_button_collection.grid(column=2, row=2, padx=10, pady=10)

new_path_label_collection = ttk.Label(tab6, text="新合集路径:")
new_path_label_collection.grid(column=0, row=7, padx=10, pady=10, sticky='w')
new_path_entry_collection = ttk.Entry(tab6, width=50)
new_path_entry_collection.grid(column=1, row=7)

fetch_collections_button = ttk.Button(tab6, text="从用户主页获取合集/播放列表", command=fetch_and_display_collections)
fetch_collections_button.grid(column=1, row=9, padx=10, pady=10)


# 创建加载和保存按钮
button_frame = ttk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

load_button = ttk.Button(button_frame, text="加载配置", command=load_config)
load_button.grid(column=0, row=0, padx=10, pady=10)

import_button = ttk.Button(button_frame, text="导入配置", command=import_config)
import_button.grid(column=1, row=0, padx=10, pady=10)

save_button = ttk.Button(button_frame, text="保存更改", command=save_config)
save_button.grid(column=2, row=0, padx=10, pady=10)

root.mainloop()
