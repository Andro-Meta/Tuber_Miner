import os
import traceback
import threading
import time
from tkinter import *
from tkinter import ttk, messagebox
import yt_dlp
from moviepy.editor import *

def start_download():
    threading.Thread(target=download_video).start()

def display_error(error_message):
    error_win = Toplevel(root)
    error_win.title("Error Details")
    error_win.geometry("600x200")

    error_text = Text(error_win, wrap=WORD, height=10, width=70)
    error_text.pack(padx=10, pady=10)
    error_text.insert(INSERT, error_message)
    error_text.config(state=DISABLED)

    close_button = Button(error_win, text="Close", command=error_win.destroy)
    close_button.pack(pady=10)

def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def progress_function(d):
    if d['status'] == 'downloading':
        p = d['_percent_str'].replace('%','')
        progress_percentage = float(p) * 0.5  # Only fill up to 70% for download
        root.after(1, update_progress_bar, progress_percentage)

def update_progress_bar(value):
    progress_bar['value'] = value
    root.update_idletasks()

def fetch_duration():
    url = url_entry.get()
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_duration = int(info['duration'])

    start_slider.config(to=video_duration, label=f"Start Time ({seconds_to_hms(0)})")
    end_slider.config(to=video_duration, from_=start_slider.get(), label=f"End Time ({seconds_to_hms(video_duration)})")

def update_start_label(val):
    start_slider.config(label=f"Start Time ({seconds_to_hms(float(val))})")

def update_end_label(val):
    end_slider.config(label=f"End Time ({seconds_to_hms(float(val))})")

def download_video():
    try:
        url = url_entry.get()
        choice = download_option_var.get()
        format_choice = format_option_var.get()

        ydl_opts = {
            'outtmpl': 'temp_video.%(ext)s',
            'quiet': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'progress_hooks': [progress_function],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            progress_bar['value'] = 50
            root.update_idletasks()
            info = ydl.extract_info(url, download=False)
            video_title = info['title']
            filename = ydl.prepare_filename(info)  # Get the actual filename

        clip = None
        if choice == 1:
            clip = VideoFileClip(filename)
        elif choice == 2:
            start_time = start_slider.get()
            end_time = end_slider.get()
            clip = VideoFileClip(filename).subclip((0, 0, int(start_time)), (0, 0, int(end_time)))

        if format_choice == 1:  # mp4
            clip.write_videofile(f"{video_title}.mp4", logger=None)
            output_format = "mp4"
        elif format_choice == 2:  # mp3
            clip.audio.write_audiofile(f"{video_title}.mp3", logger=None)
            output_format = "mp3"
        elif format_choice == 3:  # wav
            clip.audio.write_audiofile(f"{video_title}.wav", logger=None)
            output_format = "wav"

        if clip:
            clip.close()  # Close the VideoFileClip object

        # Retry the deletion
        for _ in range(5):  # Try 5 times
            try:
                os.remove(filename)
                break  # If successful, break out of the loop
            except PermissionError:
                time.sleep(1)  # Wait for 1 second before trying again

        progress_bar['value'] = 100
        root.update_idletasks()
        result_label.config(text=f"{video_title}.{output_format} has been saved!")
    
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}\n{traceback.format_exc()}"
        result_label.config(text="Error occurred!")
        display_error(error_message)


# GUI setup
root = Tk()
root.iconbitmap(r'E:\youtube_extractor_gui\vs.ico')
root.title("Tube Miner")
root.geometry("650x600")

url_label = Label(root, text="Enter YouTube URL:")
url_label.pack(pady=10)
url_entry = Entry(root, width=60)
url_entry.pack(pady=10)
fetch_button = Button(root, text="Fetch Video Info", command=fetch_duration)
fetch_button.pack(pady=10)

download_option_var = IntVar()
full_video_radio = Radiobutton(root, text="Download Full Video", variable=download_option_var, value=1)
segment_video_radio = Radiobutton(root, text="Download Segment", variable=download_option_var, value=2)
full_video_radio.pack(pady=5)
segment_video_radio.pack(pady=5)

start_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=500, command=update_start_label)
start_slider.pack(pady=10)
end_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=500, command=update_end_label)
end_slider.pack(pady=10)

format_option_var = IntVar()
mp4_radio = Radiobutton(root, text="MP4", variable=format_option_var, value=1)
mp3_radio = Radiobutton(root, text="MP3", variable=format_option_var, value=2)
wav_radio = Radiobutton(root, text="WAV", variable=format_option_var, value=3)
mp4_radio.pack(pady=5)
mp3_radio.pack(pady=5)
wav_radio.pack(pady=5)

progress_label = Label(root, text="Progress:")
progress_label.pack(pady=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Paste", command=lambda: url_entry.event_generate("<<Paste>>"))
url_entry.bind("<Button-3>", show_context_menu)

download_button = Button(root, text="Download", command=start_download)
download_button.pack(pady=20)

result_label = Label(root, text="")
result_label.pack(pady=10)

root.mainloop()
