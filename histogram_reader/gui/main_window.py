"""Main window for the HistogramReader application."""

import os
import tempfile
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

import numpy as np
import plotly.graph_objects as go


class FileManagerPanel(ttk.Frame):
    """Left panel for file and folder selection."""

    def __init__(self, parent, **kwargs):
        """Initialize the file manager panel."""
        super().__init__(parent, **kwargs)
        self.data_service = None  # Will be set by parent
        self.plot_panel = None  # Will be set by parent
        self.setup_ui()

    def get_root_window(self):
        """Get the root window (Tk instance) of this widget."""
        widget = self
        while hasattr(widget, "master") and widget.master:
            widget = widget.master
        return widget

    def setup_ui(self):
        """Set up the file manager UI components."""
        # Title
        title_label = tk.Label(
            self, text="File Manager", font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=(10, 20), padx=10, anchor="w")

        # File selection buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.select_file_btn = ttk.Button(
            button_frame, text="📄 Select File", command=self.select_file, width=15
        )
        self.select_file_btn.pack(fill="x", pady=2)

        self.select_folder_btn = ttk.Button(
            button_frame, text="📁 Select Folder", command=self.select_folder, width=15
        )
        self.select_folder_btn.pack(fill="x", pady=2)

        # File Explorer Section
        explorer_frame = ttk.LabelFrame(self, text="File Explorer", padding=10)
        explorer_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Treeview for file explorer
        self.file_tree = ttk.Treeview(
            explorer_frame, columns=("name", "type", "size"), show="tree headings"
        )

        # Configure columns
        self.file_tree.heading("#0", text="Path", anchor="w")
        self.file_tree.heading("name", text="Name", anchor="w")
        self.file_tree.heading("type", text="Type", anchor="w")
        self.file_tree.heading("size", text="Size", anchor="w")

        self.file_tree.column("#0", width=200, minwidth=100)
        self.file_tree.column("name", width=150, minwidth=100)
        self.file_tree.column("type", width=80, minwidth=50)
        self.file_tree.column("size", width=80, minwidth=50)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(
            explorer_frame, orient="vertical", command=self.file_tree.yview
        )
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind double-click event for file selection
        self.file_tree.bind("<Double-1>", self.on_file_double_click)

        # Selected File Section
        selected_frame = ttk.LabelFrame(self, text="Selected File", padding=10)
        selected_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Selected file info
        self.selected_file_label = tk.Label(
            selected_frame, text="No file selected", font=("Helvetica", 10)
        )
        self.selected_file_label.pack(anchor="w", pady=(0, 10))

        # Channel list for selected file
        self.channel_listbox = tk.Listbox(selected_frame, height=8, selectmode="single")
        self.channel_listbox.pack(fill="both", expand=True)

        # Bind channel selection event
        self.channel_listbox.bind("<<ListboxSelect>>", self.on_channel_select)

        # Control buttons
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=5)

        self.load_btn = ttk.Button(
            control_frame,
            text="📊 Load Selected",
            command=self.load_selected_file,
            width=15,
        )
        self.load_btn.pack(fill="x", pady=2)

        self.clear_btn = ttk.Button(
            control_frame, text="🗑️ Clear All", command=self.clear_files, width=15
        )
        self.clear_btn.pack(fill="x", pady=2)

    def select_file(self):
        """Handle file selection."""
        if not self.data_service:
            messagebox.showwarning(
                "Warning", "Data service not available. Please restart the application."
            )
            return

        # Use a simpler filetypes format that works on macOS
        filetypes = [
            ("All supported files", "*.csv *.txt *.dat"),
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("Data files", "*.dat"),
            ("All files", "*"),
        ]

        try:
            # Force the dialog to be modal and handle potential macOS issues
            root = self.get_root_window()
            root.update()  # Ensure the main window is ready

            files = filedialog.askopenfilenames(
                title="Select histogram data files",
                filetypes=filetypes,
                parent=root,  # Ensure proper parent window
            )

            if files:
                for file_path in files:
                    self.add_file_to_tree(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file dialog: {str(e)}")
            print(f"File dialog error: {e}")
            # Try fallback approach for macOS
            try:
                print("Attempting fallback file dialog...")
                files = filedialog.askopenfilenames(
                    title="Select histogram data files (fallback)", parent=root
                )
                if files:
                    for file_path in files:
                        self.add_file_to_tree(file_path)
            except Exception as fallback_e:
                messagebox.showerror(
                    "Error", f"Fallback dialog also failed: {str(fallback_e)}"
                )
                print(f"Fallback dialog error: {fallback_e}")

    def select_folder(self):
        """Handle folder selection."""
        if not self.data_service:
            messagebox.showwarning(
                "Warning", "Data service not available. Please restart the application."
            )
            return

        try:
            # Force the dialog to be modal and handle potential macOS issues
            root = self.get_root_window()
            root.update()  # Ensure the main window is ready

            folder = filedialog.askdirectory(
                title="Select folder containing histogram data",
                parent=root,  # Ensure proper parent window
            )
            if folder:
                # Scan folder for supported files
                files = self.data_service.scan_folder(folder)
                for file_path in files:
                    self.add_file_to_tree(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder dialog: {str(e)}")
            print(f"Folder dialog error: {e}")
            # Try fallback approach for macOS
            try:
                print("Attempting fallback folder dialog...")
                folder = filedialog.askdirectory(
                    title="Select folder containing histogram data (fallback)",
                    parent=root,
                )
                if folder:
                    files = self.data_service.scan_folder(folder)
                    for file_path in files:
                        self.add_file_to_tree(file_path)
            except Exception as fallback_e:
                messagebox.showerror(
                    "Error", f"Fallback folder dialog also failed: {str(fallback_e)}"
                )
                print(f"Fallback folder dialog error: {fallback_e}")

    def add_file_to_tree(self, file_path: str):
        """Add a file to the tree view."""
        try:
            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return

            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].upper()

            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024**2:
                size_str = f"{file_size/1024:.1f} KB"
            elif file_size < 1024**3:
                size_str = f"{file_size/(1024**2):.1f} MB"
            else:
                size_str = f"{file_size/(1024**3):.1f} GB"

            self.file_tree.insert(
                "", "end", text=file_path, values=(file_name, file_ext, size_str)
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not add file {file_path}: {str(e)}")
            print(f"Error adding file to tree: {e}")

    def add_folder_to_tree(self, folder_path: str):
        """Add a folder to the tree view."""
        folder_name = os.path.basename(folder_path)
        self.file_tree.insert(
            "", "end", text=folder_path, values=(folder_name, "FOLDER", "---")
        )

    def clear_files(self):
        """Clear all files from the tree."""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

    def on_file_double_click(self, event):
        """Handle double-click on file in tree."""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.file_tree.item(item, "text")

            # Check if it's a file (not a folder)
            if os.path.isfile(file_path):
                self.select_file_for_analysis(file_path)

    def select_file_for_analysis(self, file_path: str):
        """Select a file for analysis and display its channels."""
        if not self.data_service:
            messagebox.showwarning("Warning", "Data service not available.")
            return

        # Load the file if not already loaded
        if not self.data_service.is_file_loaded(file_path):
            if not self.data_service.load_file(file_path):
                messagebox.showerror("Error", f"Could not load file: {file_path}")
                return

        # Get file info and update UI
        file_info = self.data_service.get_file_info(file_path)
        if file_info:
            self.selected_file_label.config(
                text=f"File: {file_info['file_name']}\n"
                f"Channels: {file_info['num_channels']}\n"
                f"Bins: {file_info['num_bins']}\n"
                f"Range: {file_info['bin_range']['min']:.1f} "
                f"to {file_info['bin_range']['max']:.1f}"
            )

            # Update channel list
            self.channel_listbox.delete(0, tk.END)
            for channel in file_info["channels"]:
                self.channel_listbox.insert(tk.END, channel)
        else:
            self.selected_file_label.config(text="Error loading file info")
            self.channel_listbox.delete(0, tk.END)

    def on_channel_select(self, event):
        """Handle channel selection in the listbox."""
        selection = self.channel_listbox.curselection()
        if selection:
            channel_index = selection[0]
            channel_name = self.channel_listbox.get(channel_index)

            # Get the currently selected file
            file_selection = self.file_tree.selection()
            if file_selection and self.plot_panel:
                item = file_selection[0]
                file_path = self.file_tree.item(item, "text")

                if os.path.isfile(file_path):
                    # Plot the selected channel
                    self.plot_panel.plot_channel_data(file_path, channel_name)

    def load_selected_file(self):
        """Load the currently selected file for analysis."""
        # Get the selected file from the label
        label_text = self.selected_file_label.cget("text")
        if label_text == "No file selected":
            messagebox.showwarning("Warning", "Please select a file first.")
            return

        # Extract file path from the tree selection
        selection = self.file_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file in the explorer.")
            return

        item = selection[0]
        file_path = self.file_tree.item(item, "text")

        if os.path.isfile(file_path):
            self.select_file_for_analysis(file_path)
            messagebox.showinfo(
                "Success", f"File loaded: {os.path.basename(file_path)}"
            )
        else:
            messagebox.showwarning("Warning", "Selected item is not a file.")

    def load_data(self):
        """Load selected data files."""
        items = self.file_tree.get_children()
        if not items:
            messagebox.showwarning("Warning", "No files selected to load.")
            return

        # For now, just show a message
        messagebox.showinfo(
            "Info",
            f"Would load {len(items)} files/folders.\n"
            "(Functionality to be implemented)",
        )


class PlotPanel(ttk.Frame):
    """Right panel for interactive plots."""

    def __init__(self, parent, **kwargs):
        """Initialize the plot panel."""
        super().__init__(parent, **kwargs)
        self.current_plot_file = None
        self.data_service = None  # Will be set by parent
        self.current_file_path = None
        self.current_channel = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the plot panel UI components."""
        # Title and controls
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        title_label = tk.Label(
            header_frame,
            text="Interactive Histogram Viewer",
            font=("Helvetica", 14, "bold"),
        )
        title_label.pack(side="left")

        # Plot control buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side="right")

        self.refresh_btn = ttk.Button(
            button_frame, text="🔄 Refresh", command=self.refresh_plot, width=10
        )
        self.refresh_btn.pack(side="left", padx=2)

        self.save_btn = ttk.Button(
            button_frame, text="💾 Save Plot", command=self.save_plot, width=10
        )
        self.save_btn.pack(side="left", padx=2)

        self.export_btn = ttk.Button(
            button_frame, text="📤 Export", command=self.export_plot, width=10
        )
        self.export_btn.pack(side="left", padx=2)

        # Plot area frame
        self.plot_frame = ttk.LabelFrame(self, text="Histogram Plot", padding=10)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Placeholder for plot
        self.plot_placeholder = tk.Label(
            self.plot_frame,
            text="📊 No plot loaded\n\n"
            "To view a histogram:\n"
            "1. Select a file in the File Manager\n"
            "2. Choose a channel from the list\n"
            "3. The plot will automatically focus on data regions\n"
            "4. Use zoom and pan to explore the full range\n\n"
            "Features available:\n"
            "• Smart axis scaling to focus on data\n"
            "• Zoom in/out with mouse wheel\n"
            "• Pan by clicking and dragging\n"
            "• Hover over points to see values\n"
            "• Range slider for easy navigation",
            font=("Helvetica", 11),
            anchor="center",
            justify="center",
        )
        self.plot_placeholder.pack(expand=True, fill="both")

    def display_plot(self, fig):
        """Display a plotly figure in the browser."""
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as f:
                fig.write_html(f.name, include_plotlyjs="cdn")
                self.current_plot_file = f.name

            # Open in default browser
            webbrowser.open(f"file://{self.current_plot_file}")

            # Update placeholder text
            self.plot_placeholder.config(
                text="📊 Plot opened in your default browser\n\n"
                "The interactive plot is now available with:\n"
                "• Zoom and pan functionality\n"
                "• Hover tooltips showing values\n"
                "• Download options in the plot toolbar\n"
                "• Full screen mode\n\n"
                "Close the browser tab when done viewing."
            )

        except Exception as e:
            messagebox.showerror("Plot Error", f"Could not display plot: {str(e)}")

    def refresh_plot(self):
        """Refresh the current plot."""
        messagebox.showinfo("Info", "Plot refresh functionality to be implemented")

    def save_plot(self):
        """Save the current plot."""
        if self.current_plot_file:
            save_path = filedialog.asksaveasfilename(
                title="Save plot as",
                defaultextension=".html",
                filetypes=[
                    ("HTML files", "*.html"),
                    ("PNG images", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                ],
            )
            if save_path:
                try:
                    # Copy current plot file to save location
                    import shutil

                    shutil.copy2(self.current_plot_file, save_path)
                    messagebox.showinfo("Success", f"Plot saved to {save_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save plot: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No plot to save")

    def export_plot(self):
        """Export plot in various formats."""
        messagebox.showinfo("Info", "Advanced export functionality to be implemented")

    def plot_channel_data(self, file_path: str, channel_name: str):
        """Plot histogram data for a specific channel.

        Args:
            file_path: Path to the file containing the data
            channel_name: Name of the channel to plot
        """
        if not self.data_service or not self.data_service.is_file_loaded(file_path):
            messagebox.showwarning(
                "Warning", "File not loaded. Please load the file first."
            )
            return

        # Get channel data
        channel_data = self.data_service.get_channel_data(file_path, channel_name)
        if not channel_data:
            messagebox.showerror(
                "Error", f"Could not get data for channel {channel_name}"
            )
            return

        bin_values, histogram_values = channel_data

        # Create histogram plot
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=bin_values,
                y=histogram_values,
                name=f"{channel_name}",
                marker_color="rgba(55, 128, 191, 0.7)",
                marker_line_color="rgba(55, 128, 191, 1.0)",
                marker_line_width=1,
            )
        )

        # Update layout
        fig.update_layout(
            title={
                "text": f"Histogram: {channel_name}",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16},
            },
            xaxis_title="Bin Value",
            yaxis_title="Count",
            template="plotly_white",
            hovermode="closest",
            showlegend=True,
            margin=dict(l=50, r=50, t=50, b=50),
        )

        # Add hover information
        fig.update_traces(
            hovertemplate="<b>Bin:</b> %{x}<br>"
            + "<b>Count:</b> %{y}<br>"
            + "<extra></extra>"
        )

        # Implement smart axis scaling to show only data region initially
        # Find the region with actual data (non-zero values)
        data_indices = np.where(histogram_values > 0)[0]

        if len(data_indices) > 0:
            # Calculate the data region bounds
            data_start_idx = data_indices[0]
            data_end_idx = data_indices[-1]

            # Add some padding around the data region (10% of data width)
            data_width = data_end_idx - data_start_idx
            padding = max(1, int(data_width * 0.1))

            # Set initial view to focus on data region
            x_range_start = max(0, data_start_idx - padding)
            x_range_end = min(len(bin_values) - 1, data_end_idx + padding)

            # Update layout with smart axis ranges
            fig.update_layout(
                xaxis=dict(
                    range=[bin_values[x_range_start], bin_values[x_range_end]],
                    # Allow zooming out to full range
                    autorange=False,
                ),
                yaxis=dict(
                    # Auto-scale y-axis to show data clearly
                    autorange=True
                ),
            )

            # Add range slider to allow easy navigation
            fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="linear"))

        # Display the plot
        self.display_plot(fig)

        # Update current file and channel
        self.current_file_path = file_path
        self.current_channel = channel_name

        # Update placeholder text
        self.plot_placeholder.config(
            text=f"📊 Plotting: {channel_name}\n\n"
            "The interactive plot is now available with:\n"
            "• Zoom and pan functionality\n"
            "• Hover tooltips showing values\n"
            "• Download options in the plot toolbar\n"
            "• Full screen mode\n\n"
            "Close the browser tab when done viewing."
        )


class HistogramReaderApp:
    """Main application class for HistogramReader."""

    def __init__(self):
        """Initialize the application."""
        self.root = None
        self.file_manager = None
        self.plot_panel = None

        # Initialize data service
        try:
            from histogram_reader.services import DataReaderService

            self.data_service = DataReaderService()
        except ImportError:
            self.data_service = None
            print("Warning: DataReaderService not available")
        except Exception as e:
            self.data_service = None
            print(f"Warning: Could not initialize DataReaderService: {e}")

    def create_ui(self):
        """Create the main user interface."""
        # Create main window with standard tkinter
        self.root = tk.Tk()
        self.root.title("HistogramReader - FIT Detector Data Analysis")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)

        # Configure window icon (if available)
        try:
            # Try to set icon from assets folder
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "logo.ico"
            )
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except (tk.TclError, OSError):
            # Icon file not found or invalid format - continue without icon
            # This is expected behavior and not an error condition
            pass

        # Create main container with paned window
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel - File Manager (30% width)
        self.file_manager = FileManagerPanel(main_paned, padding=10)
        self.file_manager.data_service = self.data_service
        main_paned.add(self.file_manager, weight=3)

        # Right panel - Plot Area (70% width)
        self.plot_panel = PlotPanel(main_paned, padding=10)
        self.plot_panel.data_service = self.data_service
        main_paned.add(self.plot_panel, weight=7)

        # Connect the panels
        self.file_manager.plot_panel = self.plot_panel

        # Create menu bar
        self.create_menu()

        # Create status bar
        self.create_status_bar()

        # Center window on screen
        self.center_window()

    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="Open File...", command=self.file_manager.select_file
        )
        file_menu.add_command(
            label="Open Folder...", command=self.file_manager.select_folder
        )
        file_menu.add_separator()
        file_menu.add_command(label="Save Plot...", command=self.plot_panel.save_plot)
        file_menu.add_command(label="Export...", command=self.plot_panel.export_plot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(
            label="Refresh Plot", command=self.plot_panel.refresh_plot
        )
        view_menu.add_command(
            label="Clear Files", command=self.file_manager.clear_files
        )

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_bar = tk.Label(
            self.root,
            text="Ready - Select files to begin histogram analysis",
            relief="sunken",
            anchor="w",
            bd=1,
        )
        self.status_bar.pack(side="bottom", fill="x")

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def show_about(self):
        """Show about dialog."""
        about_text = """HistogramReader v1.0.0

FIT Detector Histogram Analysis Tool

Features:
• Interactive histogram visualization
• Multiple file format support
• Modern, responsive interface
• Export capabilities
• Zoom, pan, and hover functionality

Developed for CERN FIT Detector Toolkit
© 2024 Mateusz Polis"""

        messagebox.showinfo("About HistogramReader", about_text)

    def run(self):
        """Start the application."""
        self.create_ui()

        # Update status bar
        self.status_bar.config(
            text="Application started - Select files to begin histogram analysis"
        )

        # Start the main event loop
        self.root.mainloop()

        # Cleanup temporary files
        if (
            hasattr(self.plot_panel, "current_plot_file")
            and self.plot_panel.current_plot_file
        ):
            try:
                os.unlink(self.plot_panel.current_plot_file)
            except OSError:
                # Temporary file already deleted or permission denied
                # This is not a critical error during cleanup
                pass
