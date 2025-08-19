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
        self.setup_ui()

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

        # File list area
        list_frame = ttk.LabelFrame(self, text="Selected Files", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview for file list
        self.file_tree = ttk.Treeview(
            list_frame, columns=("name", "type", "size"), show="tree headings"
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
            list_frame, orient="vertical", command=self.file_tree.yview
        )
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Control buttons
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=5)

        self.clear_btn = ttk.Button(
            control_frame, text="🗑️ Clear All", command=self.clear_files, width=15
        )
        self.clear_btn.pack(fill="x", pady=2)

        self.load_btn = ttk.Button(
            control_frame, text="📊 Load Data", command=self.load_data, width=15
        )
        self.load_btn.pack(fill="x", pady=2)

    def select_file(self):
        """Handle file selection."""
        filetypes = [
            ("All supported", "*.csv;*.txt;*.dat;*.parquet;*.h5;*.hdf5"),
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("Data files", "*.dat"),
            ("Parquet files", "*.parquet"),
            ("HDF5 files", "*.h5;*.hdf5"),
            ("All files", "*.*"),
        ]

        files = filedialog.askopenfilenames(
            title="Select histogram data files", filetypes=filetypes
        )

        if files:
            for file_path in files:
                self.add_file_to_tree(file_path)

    def select_folder(self):
        """Handle folder selection."""
        folder = filedialog.askdirectory(
            title="Select folder containing histogram data"
        )
        if folder:
            # For now, just add the folder to the tree
            # Later we'll scan for supported files
            self.add_folder_to_tree(folder)

    def add_file_to_tree(self, file_path: str):
        """Add a file to the tree view."""
        try:
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
        self.setup_ui()
        self.create_sample_plot()

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
            text="📊 Interactive plot will appear here\n\n"
            "Features available:\n"
            "• Zoom in/out with mouse wheel\n"
            "• Pan by clicking and dragging\n"
            "• Hover over points to see values\n"
            "• Use toolbar for additional options\n"
            "• Export plots in various formats",
            font=("Helvetica", 11),
            anchor="center",
            justify="center",
        )
        self.plot_placeholder.pack(expand=True, fill="both")

    def create_sample_plot(self):
        """Create a sample histogram plot to demonstrate functionality."""
        # Generate sample histogram data
        np.random.seed(42)
        data = np.random.normal(100, 15, 1000)

        # Create histogram
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=data,
                nbinsx=30,
                name="Sample Histogram",
                marker_color="rgba(55, 128, 191, 0.7)",
                marker_line_color="rgba(55, 128, 191, 1.0)",
                marker_line_width=1,
            )
        )

        # Update layout for better appearance
        fig.update_layout(
            title={
                "text": "Sample Histogram Data",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16},
            },
            xaxis_title="Value",
            yaxis_title="Frequency",
            template="plotly_white",
            hovermode="closest",
            showlegend=True,
            margin=dict(l=50, r=50, t=50, b=50),
        )

        # Add hover information
        fig.update_traces(
            hovertemplate="<b>Value Range:</b> %{x}<br>"
            + "<b>Count:</b> %{y}<br>"
            + "<extra></extra>"
        )

        # Save plot to temporary file and open in browser
        self.display_plot(fig)

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


class HistogramReaderApp:
    """Main application class for HistogramReader."""

    def __init__(self):
        """Initialize the application."""
        self.root = None
        self.file_manager = None
        self.plot_panel = None

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
        main_paned.add(self.file_manager, weight=3)

        # Right panel - Plot Area (70% width)
        self.plot_panel = PlotPanel(main_paned, padding=10)
        main_paned.add(self.plot_panel, weight=7)

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
            text="Ready - Select files or folders to begin analysis",
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
        self.status_bar.config(text="Application started - Ready for data analysis")

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
