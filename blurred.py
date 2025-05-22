import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import face  
from license import run_license_algorithm
from PIL import Image, ImageTk
from PIL import Image
import piexif
from exif_utils import get_full_exif_data, add_exif_to_image
import os
import time

class ImageProcessingTool:
    def __init__(self, master):
        self.master = master
        # Load and set the application icon
        self.icon_image = Image.open(r"C:\Users\Souran Jash\Documents\6.Droneview\3.final\Final code set\assets\logo3.png")
        self.icon_image = self.icon_image.resize((50, 50), Image.Resampling.LANCZOS)  # Resize to a suitable icon size
        self.icon_photo = ImageTk.PhotoImage(self.icon_image)
        self.master.iconphoto(True, self.icon_photo)  # Set the window icon
        
        self.master.title("Image Processing Tool")
        self.master.geometry("550x650")

        # Center the window on the screen
        window_width, window_height = 550, 650
        screen_width, screen_height = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)- 30
        self.master.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        self.folder_path = ""
        self.selected_algorithms = []
        self.is_processing = False
        self.ok_button = None

        # Folder selection button
        self.select_button = tk.Button(
                                    master,
                                    text="Select Image Folder",
                                    command=self.select_folder,
                                    width=50,  # Set the desired width
                                    bg="#1F54C4",  # Default background color
                                    activebackground="#0A0045",  # Background color on hover
                                    fg="white",  # Text color
                                    font=("Sora", 10, "bold"),
                                    highlightbackground="#1F54C4",  # Background color when button is not focused
                                    highlightthickness=0,  # No border thickness for highlight
                                    
                                )
        self.select_button.pack(pady=(20, 10))

        # Label to display the selected folder path
        self.folder_label = tk.Label(master, text="", wraplength=350)
        self.folder_label.pack(pady=5)


        # Main frame with 1px border to act as a "box"
        # Label for Algorithm Selection
        self.label = tk.Label(
            master,
            text="Algorithm Selection:",
            font=("Sora", 10, "bold"),  # Bold font
            fg="#000000"  # Text color
        )
        self.label.pack(pady=5)

        # Frame for checkboxes to arrange them horizontally
        self.checkbox_frame = tk.Frame(master)
        self.checkbox_frame.pack(pady=5)

        # Algorithm selection options
        self.face_var = tk.BooleanVar()
        self.license_var = tk.BooleanVar()

        # Face Algorithm Checkbox
        self.face_check = tk.Checkbutton(
            self.checkbox_frame,
            text="Face Algorithm",
            variable=self.face_var,
            command=self.activate_reset_button
        )
        self.face_check.pack(side=tk.LEFT, padx=5)  # Side by side with padding

        # License Algorithm Checkbox
        self.license_check = tk.Checkbutton(
            self.checkbox_frame,
            text="License Plate Algorithm",
            variable=self.license_var,
            command=self.activate_reset_button
        )
        self.license_check.pack(side=tk.LEFT, padx=5)


        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)


        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        # Process and Reset buttons inside the frame
        self.process_button = tk.Button(
            self.button_frame,
            text="Process Images",
            command=self.start_processing,
            width=50,  # Set button width
            bg="#1F54C4",  # Process button color
            fg="white" , # Text color
            font=("Sora", 10, "bold"),
        )
        self.process_button.pack(pady=5)  # Vertical arrangement with padding

        self.reset_button = tk.Button(
        self.button_frame,
        text="Reset",
        command=self.reset_tool,
        state=tk.DISABLED,
        width=50,  # Set button width
        bg="#767676",  # Reset button color
        fg="white",  # Text color
        activeforeground="white",  # Text color when hovered
        disabledforeground="#B0B0B0",  # Color for disabled text
        font=("Sora", 10, "bold"),
    )
        self.reset_button.pack(pady=10)

        # Progress bars (hidden initially)
        self.face_progress = ttk.Progressbar(master, orient="horizontal", mode="determinate", length=400)
        self.license_progress = ttk.Progressbar(master, orient="horizontal", mode="determinate", length=400)
        self.face_progress_label = tk.Label(master, text="")
        self.license_progress_label = tk.Label(master, text="")
        self.face_processed_label = tk.Label(master, text="")
        self.license_processed_label = tk.Label(master, text="")
        # Initialize canvases
        self.face_progress_canvas = None
        self.license_progress_canvas = None

        # Frame for success message with a border (hidden initially)
        self.success_frame = tk.Frame(master, borderwidth=1, relief="solid")
        self.success_frame.pack(pady=(10, 5), padx=10)  # Add padding around the frame
        self.success_frame.config(bg="#FFFFFF", highlightbackground="#1F54C4", highlightthickness=1)  # Set the background color of the frame and border color

        # Create a label to display the success message inside the frame
        self.success_label = tk.Label(self.success_frame, text="", fg='#000000', font=("Sora", 10, "bold"), bg="#FFFFFF")
        self.success_label.pack(pady=10, padx=10)  # Add padding inside the frame

        # Hide the success frame initially
        self.success_frame.pack_forget()


        # Load and display the IO logo images at the bottom corners
        # Load logo images
        self.logo1 = Image.open(r"C:\Users\Souran Jash\Documents\6.Droneview\3.final\Final code set\assets\logo1.png")
        self.logo2 = Image.open(r"C:\Users\Souran Jash\Documents\6.Droneview\3.final\Final code set\assets\logo2.png")

        # Resize images to fit your layout
        self.logo1 = self.logo1.resize((150, 30), Image.Resampling.LANCZOS)
        self.logo2 = self.logo2.resize((100, 30), Image.Resampling.LANCZOS)

        # Create PhotoImage objects
        self.logo1_photo = ImageTk.PhotoImage(self.logo1)
        self.logo2_photo = ImageTk.PhotoImage(self.logo2)

        # Create labels for logos and position them
        self.logo1_label = tk.Label(master, image=self.logo1_photo)  # Set a background color if needed
        self.logo1_label.place(relx=0.05, rely=0.98, anchor='sw')  # Reduced left margin (relx from 0.1 to 0.05) and bottom margin

        self.logo2_label = tk.Label(master, image=self.logo2_photo)  # Set a background color if needed
        self.logo2_label.place(relx=0.95, rely=0.98, anchor='se')  # Reduced right margin (relx from 0.9 to 0.85) and bottom margin

        

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.config(text=f"Selected Folder: {self.folder_path}", fg="#656565")
            self.activate_reset_button()

    def activate_reset_button(self):
        """Enable the reset button when changes occur."""
        self.reset_button.config(state=tk.NORMAL)

    def start_processing(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder Selected", "Please select a folder with images.")
            return

        self.selected_algorithms = []
        if self.face_var.get():
            self.selected_algorithms.append("Face")
        if self.license_var.get():
            self.selected_algorithms.append("License")

        if not self.selected_algorithms:
            messagebox.showwarning("No Algorithm Selected", "Please select at least one algorithm.")
            return

        self.toggle_ui_elements(state=tk.DISABLED)
       
        threading.Thread(target=self.process_images).start()

    def process_images(self):
        try:
            # Determine which algorithms to run
            if "Face" in self.selected_algorithms and "License" in self.selected_algorithms:
                self.run_face_and_license_algorithms()
            elif "Face" in self.selected_algorithms:
                self.run_face_algorithm_alone()
            elif "License" in self.selected_algorithms:
                self.run_license_algorithm_alone()

            self.show_success_message()
        except Exception as e:
            messagebox.showerror("Processing Error", f"Error during processing: {e}")
            print("Processing Error", f"Error during processing: {e}")
        finally:
            self.toggle_ui_elements(state=tk.NORMAL)



    def run_face_algorithm(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Error reading image: {image_path}")
        return face.process_image(image)


    def run_face_algorithm_alone(self):
        # Define the backup folder path
        backup_folder = f"{self.folder_path}_Backup"

        # Ensure the backup folder is created if it doesn't exist
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # Define the log file path (in the backup folder)
        log_file_path = os.path.join(backup_folder, f"{os.path.basename(self.folder_path)}_log_file.txt")

        # Ensure the log file is created only if it doesn't already exist
        if not os.path.exists(log_file_path):
            with open(log_file_path, "w") as log_file:
                log_file.write("Face & License Detection Log\n")  # Write a header line

        image_files = self.get_image_files(self.folder_path)  # Get images from the original folder
        self.setup_face_progress_bar(len(image_files))

        for i, file_name in enumerate(image_files):
            image_path = os.path.join(self.folder_path, file_name)
            backup_image_path = os.path.join(backup_folder, file_name)

            # Step 1: Extract EXIF data from the original image
            exif_data = get_full_exif_data(image_path)

            # Step 2: Process the image with the face detection algorithm
            blurred_image, face_detected, face_coordinates = self.run_face_algorithm(image_path)
            print(face_coordinates)
            print(f"Faces detected: {face_detected}")

            # Step 3: Write detected faces and coordinates to the log file
            if face_detected and face_coordinates:
                with open(log_file_path, "a") as log_file:
                    # log_file.write(f"**{file_name} : Face**\n")  # Image name and "Face" in bold
                    for idx, face_coord_string in enumerate(face_coordinates):
                        log_file.write(f"{file_name}: {face_coord_string}\n") 

            # Step 4: Handle backup and image processing logic
            if os.path.exists(backup_image_path):
                # Original image is already in the backup folder
                if face_detected:
                    # Save the blurred image in the original folder
                    output_path = os.path.join(self.folder_path, file_name)
                    cv2.imwrite(output_path, blurred_image)
                    add_exif_to_image(output_path, exif_data)
                    
                # Do nothing if face detection is false
            else:
                # Original image is NOT in the backup folder
                if face_detected:
                    # Move the original image to the backup folder
                    shutil.move(image_path, backup_image_path)
                    # Save the blurred image in the original folder
                    output_path = os.path.join(self.folder_path, file_name)
                    cv2.imwrite(output_path, blurred_image)
                    add_exif_to_image(output_path, exif_data)
                    
                # Do nothing if face detection is false

            # Step 5: Update the progress bar
            self.update_face_progress(i + 1, len(image_files))



    def run_license_algorithm_alone(self):
        # Define the backup folder path
        backup_folder = f"{self.folder_path}_Backup"

        # Ensure the backup folder is created if it doesn't exist
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # Define the log file path inside the backup folder
        log_file_path = os.path.join(backup_folder, f"{os.path.basename(self.folder_path)}_log_file.txt")

        # Ensure the log file is created only if it doesn't already exist
        if not os.path.exists(log_file_path):
            with open(log_file_path, "w") as log_file:
                log_file.write("Face & License Detection Log\n")  # Write a header line

        image_files = self.get_image_files(self.folder_path)  # Get images from the original folder
        self.setup_license_progress_bar(len(image_files))

        for i, file_name in enumerate(image_files):
            image_path = os.path.join(self.folder_path, file_name)
            backup_image_path = os.path.join(backup_folder, file_name)

            # Step 1: Extract EXIF data from the original image
            exif_data = get_full_exif_data(image_path)

            # Step 2: Process the image with the license plate algorithm
            blurred_image, license_plate_detected, license_coordinates = run_license_algorithm(image_path, "license_plate_detector.pt")
            print(f"License Plate detected: {license_plate_detected}")

            # Step 3: Write detected license plates and coordinates to the log file
            if license_plate_detected and license_coordinates:
                with open(log_file_path, "a") as log_file:
                    # log_file.write(f"**{file_name} : License**\n")  # Image name and "License" in bold
                    for idx, license_coords in enumerate(license_coordinates):
                        log_file.write(f"{file_name}: License: (X1: {license_coords['X1']}, Y1: {license_coords['Y1']}, X2: {license_coords['X2']}, Y2: {license_coords['Y2']})\n")

            # Step 4: Handle backup and image processing logic
            if os.path.exists(backup_image_path):
                # Original image is already in the backup folder
                if license_plate_detected:
                    # Save the blurred image in the original folder
                    cv2.imwrite(image_path, blurred_image)
                    add_exif_to_image(image_path, exif_data)
                    # Update the file's created at and modified at timestamps to the current time
                    current_time = time.time()
                    os.utime(image_path, (current_time, current_time))
                # Do nothing if license plate detection is false
            else:
                # Original image is NOT in the backup folder
                if license_plate_detected:
                    # Move the original image to the backup folder
                    shutil.move(image_path, backup_image_path)
                    # Save the blurred image in the original folder
                    cv2.imwrite(image_path, blurred_image)
                    add_exif_to_image(image_path, exif_data)
                    # Update the file's created at and modified at timestamps to the current time
                    current_time = time.time()
                    os.utime(image_path, (current_time, current_time))
                # Do nothing if license plate detection is false

            # Step 5: Update the progress bar
            self.update_license_progress(i + 1, len(image_files))


    
    def run_face_and_license_algorithms(self):
        # Define the backup folder path
        backup_folder = f"{self.folder_path}_Backup"

        # Ensure the backup folder is created if it doesn't exist
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # Define the log file path inside the backup folder
        log_file_path = os.path.join(backup_folder, f"{os.path.basename(self.folder_path)}_log_file.txt")

        # Ensure the log file is created only if it doesn't already exist
        if not os.path.exists(log_file_path):
            with open(log_file_path, "w") as log_file:
                log_file.write("Face and License  Detection Log\n")  # Write a header line

        image_files = self.get_image_files(self.folder_path)  # Get images from the original folder
        self.setup_face_progress_bar(len(image_files))
        self.setup_license_progress_bar(len(image_files))

        for i, file_name in enumerate(image_files):
            image_path = os.path.join(self.folder_path, file_name)
            backup_image_path = os.path.join(backup_folder, file_name)

            # Extract EXIF data from the original image
            exif_data = get_full_exif_data(image_path)

            # --- Face Detection ---
            blurred_image_face, face_detected, face_coordinates = self.run_face_algorithm(image_path)
            print(f"Faces detected: {face_detected}")
            # Log both face and license plate results
            with open(log_file_path, "a") as log_file:
                # Log face detection results
                if face_detected and face_coordinates:
                    # log_file.write(f"**{file_name} : Face**\n")
                    for idx, face_coord_string in enumerate(face_coordinates):
                        log_file.write(f"{file_name}: {face_coord_string}\n") 

            if os.path.exists(backup_image_path):
                # Original image is already in the backup folder
                if face_detected:
                    # Save the face-blurred image in the original folder
                    output_path = os.path.join(self.folder_path, file_name)
                    cv2.imwrite(output_path, blurred_image_face)
                    add_exif_to_image(output_path, exif_data)
                    
            else:
                # Original image is NOT in the backup folder
                if face_detected:
                    # Move the original image to the backup folder
                    shutil.move(image_path, backup_image_path)
                    # Save the face-blurred image in the original folder
                    output_path = os.path.join(self.folder_path, file_name)
                    cv2.imwrite(output_path, blurred_image_face)
                    add_exif_to_image(output_path, exif_data)
                    

            # --- License Plate Detection ---
            blurred_image_license, license_plate_detected, license_coordinates = run_license_algorithm(
                os.path.join(self.folder_path, file_name), "license_plate_detector.pt"
            )
            print(f"License plate detected: {license_plate_detected}")
            with open(log_file_path, "a") as log_file:
                # Log license plate detection results
                if license_plate_detected and license_coordinates:
                    # log_file.write(f"**{file_name} : License**\n")
                    for idx, license_coords in enumerate(license_coordinates):
                        log_file.write(f"{file_name}: License: (X1: {license_coords['X1']}, Y1: {license_coords['Y1']}, X2: {license_coords['X2']}, Y2: {license_coords['Y2']})\n")


            if os.path.exists(backup_image_path):
                # Original image is already in the backup folder
                if license_plate_detected:
                    # Save the license plate-blurred image in the original folder
                    output_path = os.path.join(self.folder_path, file_name)
                    cv2.imwrite(output_path, blurred_image_license)
                    add_exif_to_image(output_path, exif_data)
                    
            else:
                # Original image is NOT in the backup folder
                if license_plate_detected:
                    # Move the original image to the backup folder
                    shutil.move(image_path, backup_image_path)
                    # Save the license plate-blurred image in the original folder
                    output_path = os.path.join(self.folder_path, file_name)
                    cv2.imwrite(output_path, blurred_image_license)
                    add_exif_to_image(output_path, exif_data)
                    

           
           
            # Update progress bars
            self.update_face_progress(i + 1, len(image_files))
            self.update_license_progress(i + 1, len(image_files))



    
    
    

    def get_image_files(self, folder_path):
        return [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

    def setup_face_progress_bar(self, total_images):
        
        self.face_progress_label.config(text="Face Algorithm Running", font=("Sora", 10, "bold"))
        self.face_progress_label.pack(pady=(10, 5))  # Show label first

        # Create a canvas for the progress bar
        self.face_progress_canvas = tk.Canvas(self.master, width=400, height=30, bg="white", bd=1, relief="solid")
        self.face_progress_canvas.pack(pady=5)  # Progress bar after label

        # Initialize the progress bar rectangle with green color
        self.face_progress_bar = self.face_progress_canvas.create_rectangle(0, 0, 0, 30, fill="#0BDA51")  # Green color fills the height
        self.face_progress["maximum"] = total_images

        # Initialize the progress percentage label with initial value
        self.face_processed_label = tk.Label(self.master, text=f"0/{total_images} images processed (0.00%)", font=("Sora", 10))
        self.face_processed_label.pack(pady=5)

    def update_face_progress(self, current_image, total_images):
        self.face_progress["value"] = current_image
        percentage = (current_image / total_images) * 100

        # Update the rectangle width based on the percentage
        width = (400 * percentage) / 100  # Width of the progress bar canvas is 300
        self.face_progress_canvas.coords(self.face_progress_bar, 0, 0, width, 30)  # Update bar width to fill the height correctly

        # Update the percentage text on the canvas
        self.face_progress_canvas.delete("text")  # Clear previous text
        self.face_progress_canvas.create_text(200, 15, text=f"{percentage:.2f}%", fill="black", font=("Sora", 10, "bold"), tags="text")

        # Update the label below
        self.face_processed_label.config(text=f"{current_image}/{total_images} images processed")  # This remains as is

    def setup_license_progress_bar(self, total_images):

        

        self.license_progress_label.config(text="License Plate Algorithm Running", font=("Sora", 10, "bold"))
        self.license_progress_label.pack(pady=(10, 5))  # Show label first

        # Create a canvas for the progress bar
        self.license_progress_canvas = tk.Canvas(self.master, width=400, height=30, bg="white", bd=1, relief="solid")
        self.license_progress_canvas.pack(pady=5)  # Progress bar after label

        # Initialize the progress bar rectangle with green color
        self.license_progress_bar = self.license_progress_canvas.create_rectangle(0, 0, 0, 30, fill="#0BDA51")  # Green color fills the height
        self.license_progress["maximum"] = total_images

        # Initialize the progress percentage label with initial value
        self.license_processed_label = tk.Label(self.master, text=f"0/{total_images} images processed (0.00%)", font=("Sora", 10))
        self.license_processed_label.pack(pady=5)

    def update_license_progress(self, current_image, total_images):
        self.license_progress["value"] = current_image
        percentage = (current_image / total_images) * 100

        # Update the rectangle width based on the percentage
        width = (400 * percentage) / 100  # Width of the progress bar canvas is 300
        self.license_progress_canvas.coords(self.license_progress_bar, 0, 0, width, 30)  # Update bar width to fill the height correctly

        # Update the percentage text on the canvas
        self.license_progress_canvas.delete("text")  # Clear previous text
        self.license_progress_canvas.create_text(200, 15, text=f"{percentage:.2f}%", fill="black", font=("Sora", 10, "bold"), tags="text")

        # Update the label below
        self.license_processed_label.config(text=f"{current_image}/{total_images} images processed")  # This remains as is


    def show_success_message(self):
        total_images = len(os.listdir(self.folder_path))
        self.success_label.config(text=f"Images processed successfully! Total images: {total_images}")
        self.success_frame.pack(pady=(10, 5), padx=10)


    def toggle_ui_elements(self, state):
        # self.select_button.config(state=state)
        # self.process_button.config(state=state)
        self.face_check.config(state=state)
        self.license_check.config(state=state)

        # Update the process button's state and appearance
        self.process_button.config(state=state)
        if state == tk.NORMAL:
            self.process_button.config(bg="#1F54C4", fg="white")  # Active state
        else:
            self.process_button.config(bg="#A9A9A9", fg="#F5F5F5")  # Disabled state


        self.select_button.config(state=state)
        if state == tk.NORMAL:
            self.select_button.config(bg="#1F54C4", fg="white")  # Active state
        else:
            self.select_button.config(bg="#A9A9A9", fg="#F5F5F5")  # Disabled state


        

    def reset_tool(self):
        self.folder_path = ""
        self.folder_label.config(text="")
        self.face_var.set(False)
        self.license_var.set(False)
        self.selected_algorithms.clear()

        # Reset progress bars and hide success message
        self.reset_progress_bars()

        # Re-enable all UI elements
        self.toggle_ui_elements(state=tk.NORMAL)

        # Clear the success message and hide the frame
        self.success_label.config(text="")
        self.success_frame.pack_forget()

            

       

    def reset_progress_bars(self):
        # Reset progress bar values
        self.face_progress["value"] = 0
        self.license_progress["value"] = 0

        # Hide or remove all progress-related labels and widgets
        self.face_progress_label.pack_forget()
        self.license_progress_label.pack_forget()
        self.face_processed_label.pack_forget()
        self.license_processed_label.pack_forget()

        # Check if the canvas widgets exist, then delete them
        if self.face_progress_canvas is not None:
            self.face_progress_canvas.pack_forget()
            self.face_progress_canvas.destroy()  # Destroy the widget to free memory
            self.face_progress_canvas = None  # Reset the reference

        if self.license_progress_canvas is not None:
            self.license_progress_canvas.pack_forget()
            self.license_progress_canvas.destroy()
            self.license_progress_canvas = None

 

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingTool(root)
    root.mainloop()




