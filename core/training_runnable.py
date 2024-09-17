from PyQt5.QtCore import QRunnable
import logging


class TrainingRunnable(QRunnable):
    def __init__(self, logic, training_function, finished_signal):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logic = logic
        self.training_function = training_function
        self._is_running = True
        self.finished_signal = finished_signal  # Pass the signal directly

    def run(self):
        self.logic.current_thread = self  # This allows the logic to check if it should stop
        self.logger.debug(f"Starting training sequence: {self.training_function.__name__}")
        try:
            result = self.training_function()
            if not result:
                self.logger.debug("Training sequence ended early.")
        except Exception as e:
            self.logic.logger.error(f"Error during {self.training_function.__name__}: {str(e)}")
        finally:
            self._is_running = False
            self.logic.quicksave()
            self.logic.open_menu()
            self.logger.debug("Finished running training sequence")
            self.finished_signal.emit()  # Emit the finished signal

    def stop(self):
        self._is_running = False
        self.logger.debug("Training sequence stopped.")

