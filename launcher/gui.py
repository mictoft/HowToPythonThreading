#!/usr/bin/env python3
"""
Qt-based GUI Launcher for Python Threading Examples

This provides a graphical interface to browse and run examples.

OPTIONAL DEPENDENCY: Requires PyQt6 or PySide6
Install with: pip install PyQt6
Or: pip install PySide6
"""

import sys
import os
from pathlib import Path

# Try to import Qt
QT_AVAILABLE = False
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                  QHBoxLayout, QListWidget, QTextEdit, QPushButton,
                                  QLabel, QSplitter, QListWidgetItem, QMessageBox)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
    from PyQt6.QtGui import QFont, QTextCursor
    QT_AVAILABLE = True
    print("Using PyQt6")
except ImportError:
    try:
        from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                       QHBoxLayout, QListWidget, QTextEdit, QPushButton,
                                       QLabel, QSplitter, QListWidgetItem, QMessageBox)
        from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, Slot as pyqtSlot
        from PySide6.QtGui import QFont, QTextCursor
        QT_AVAILABLE = True
        print("Using PySide6")
    except ImportError:
        print("Error: Qt not available!")
        print("Install with: pip install PyQt6")
        print("Or: pip install PySide6")


if QT_AVAILABLE:
    # Import launcher utilities
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from launcher.cli import discover_examples


    class ExampleRunner(QThread):
        """Thread that runs an example and captures output."""

        output = pyqtSignal(str)
        finished_signal = pyqtSignal(bool, str)  # success, message

        def __init__(self, example_path: Path):
            super().__init__()
            self.example_path = example_path

        def run(self):
            """Run the example in this thread."""
            import importlib.util
            import io
            import contextlib

            try:
                # Capture stdout and stderr
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()

                with contextlib.redirect_stdout(stdout_capture), \
                     contextlib.redirect_stderr(stderr_capture):

                    # Load and run the module
                    spec = importlib.util.spec_from_file_location(
                        "running_example",
                        self.example_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Run main function
                    if hasattr(module, 'main'):
                        module.main()

                # Emit captured output
                output = stdout_capture.getvalue()
                if output:
                    self.output.emit(output)

                errors = stderr_capture.getvalue()
                if errors:
                    self.output.emit(f"\n[STDERR]\n{errors}")

                self.finished_signal.emit(True, "Example completed successfully")

            except Exception as e:
                import traceback
                error_msg = f"Error running example:\n{traceback.format_exc()}"
                self.output.emit(error_msg)
                self.finished_signal.emit(False, str(e))


    class LauncherWindow(QMainWindow):
        """Main launcher window."""

        def __init__(self):
            super().__init__()
            self.examples = discover_examples()
            self.current_runner = None
            self.init_ui()

        def init_ui(self):
            """Initialize the user interface."""
            self.setWindowTitle("Python Threading Examples Launcher")
            self.setGeometry(100, 100, 1000, 700)

            # Central widget
            central = QWidget()
            self.setCentralWidget(central)

            # Main layout
            layout = QVBoxLayout(central)

            # Title
            title = QLabel("Python Threading Learning Examples")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title.setFont(title_font)
            layout.addWidget(title)

            # Splitter for examples list and output
            splitter = QSplitter(Qt.Orientation.Horizontal)

            # Left side: Examples list
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)

            examples_label = QLabel("Select an example:")
            left_layout.addWidget(examples_label)

            self.examples_list = QListWidget()
            self.examples_list.itemDoubleClicked.connect(self.on_example_double_clicked)
            self.examples_list.currentItemChanged.connect(self.on_example_selected)

            # Populate examples list
            for example in self.examples:
                item_text = f"{example['number']}. {example['name']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, example)
                self.examples_list.addItem(item)

            left_layout.addWidget(self.examples_list)

            # Run button
            self.run_button = QPushButton("Run Example")
            self.run_button.clicked.connect(self.run_selected_example)
            self.run_button.setEnabled(False)
            left_layout.addWidget(self.run_button)

            splitter.addWidget(left_panel)

            # Right side: Output display
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)

            # Example info
            self.info_label = QLabel("Select an example to see details")
            right_layout.addWidget(self.info_label)

            # Output area
            output_label = QLabel("Output:")
            right_layout.addWidget(output_label)

            self.output_text = QTextEdit()
            self.output_text.setReadOnly(True)
            self.output_text.setFont(QFont("Courier", 9))
            right_layout.addWidget(self.output_text)

            # Clear button
            clear_button = QPushButton("Clear Output")
            clear_button.clicked.connect(self.output_text.clear)
            right_layout.addWidget(clear_button)

            splitter.addWidget(right_panel)

            # Set splitter sizes
            splitter.setSizes([300, 700])

            layout.addWidget(splitter)

            # Status bar
            self.statusBar().showMessage("Ready")

        @pyqtSlot(QListWidgetItem, QListWidgetItem)
        def on_example_selected(self, current, previous):
            """Handle example selection."""
            if current:
                example = current.data(Qt.ItemDataRole.UserRole)
                info = f"<b>{example['number']}. {example['name']}</b><br>"
                if example['docstring']:
                    info += f"{example['docstring']}<br>"
                info += f"<i>File: {example['filename']}</i>"
                self.info_label.setText(info)
                self.run_button.setEnabled(True)
            else:
                self.info_label.setText("Select an example to see details")
                self.run_button.setEnabled(False)

        @pyqtSlot(QListWidgetItem)
        def on_example_double_clicked(self, item):
            """Handle double-click on example."""
            self.run_selected_example()

        def run_selected_example(self):
            """Run the currently selected example."""
            current_item = self.examples_list.currentItem()
            if not current_item:
                return

            example = current_item.data(Qt.ItemDataRole.UserRole)

            # Clear output
            self.output_text.clear()
            self.output_text.append(f"Running: {example['name']}\n")
            self.output_text.append("=" * 70 + "\n")

            # Disable run button while running
            self.run_button.setEnabled(False)
            self.statusBar().showMessage(f"Running {example['name']}...")

            # Start runner thread
            self.current_runner = ExampleRunner(example['path'])
            self.current_runner.output.connect(self.append_output)
            self.current_runner.finished_signal.connect(self.on_example_finished)
            self.current_runner.start()

        @pyqtSlot(str)
        def append_output(self, text):
            """Append text to output area."""
            self.output_text.append(text)
            # Scroll to bottom
            cursor = self.output_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.output_text.setTextCursor(cursor)

        @pyqtSlot(bool, str)
        def on_example_finished(self, success, message):
            """Handle example completion."""
            self.output_text.append("\n" + "=" * 70)
            if success:
                self.output_text.append(f"\n✓ {message}")
                self.statusBar().showMessage("Example completed successfully", 3000)
            else:
                self.output_text.append(f"\n✗ {message}")
                self.statusBar().showMessage("Example failed", 3000)

            # Re-enable run button
            self.run_button.setEnabled(True)


def main():
    """Main entry point for GUI launcher."""
    if not QT_AVAILABLE:
        print("\nError: Qt is not installed!")
        print("This launcher requires PyQt6 or PySide6")
        print("\nInstall with:")
        print("  pip install PyQt6")
        print("Or:")
        print("  pip install PySide6")
        return 1

    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    return app.exec() if hasattr(app, 'exec') else app.exec_()


if __name__ == "__main__":
    sys.exit(main())
