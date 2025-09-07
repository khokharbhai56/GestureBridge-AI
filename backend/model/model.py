import tensorflow as tf
import numpy as np
import mediapipe as mp
import cv2
import logging
from typing import List, Tuple, Optional
from ..config import Config

logger = logging.getLogger(__name__)

class SignLanguageModel:
    def __init__(self):
        self.model = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def build_model(self) -> None:
        """
        Builds and compiles the sign language recognition model
        """
        try:
            model = tf.keras.Sequential([
                # Input layer for hand landmarks
                tf.keras.layers.Input(shape=Config.INPUT_SHAPE),
                
                # CNN layers
                tf.keras.layers.Reshape((21, 3, 1)),
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                
                # Flatten and Dense layers
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                
                # Output layer
                tf.keras.layers.Dense(Config.NUM_CLASSES, activation='softmax')
            ])
            
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            self.model = model
            logger.info("Model built successfully")
        except Exception as e:
            logger.error(f"Error building model: {str(e)}")
            raise

    def extract_hand_landmarks(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract hand landmarks from a video frame using MediaPipe
        
        Args:
            frame: Input video frame
            
        Returns:
            Normalized landmarks array or None if no hand detected
        """
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.hands.process(frame_rgb)
            
            if results.multi_hand_landmarks:
                # Get the first detected hand
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Extract and normalize landmarks
                landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
                
                return landmarks
            return None
        except Exception as e:
            logger.error(f"Error extracting hand landmarks: {str(e)}")
            return None

    def preprocess_video(self, video_path: str) -> List[np.ndarray]:
        """
        Process video file and extract hand landmarks from frames
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of landmark arrays
        """
        try:
            cap = cv2.VideoCapture(video_path)
            frames_landmarks = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                landmarks = self.extract_hand_landmarks(frame)
                if landmarks is not None:
                    frames_landmarks.append(landmarks)
                    
            cap.release()
            return frames_landmarks
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise
        finally:
            if cap.isOpened():
                cap.release()

    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
             validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None,
             epochs: int = 10, batch_size: int = 32) -> tf.keras.callbacks.History:
        """
        Train the model on the provided data
        
        Args:
            X_train: Training features
            y_train: Training labels
            validation_data: Optional tuple of validation features and labels
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
            
        try:
            history = self.model.fit(
                X_train,
                y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=validation_data,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(
                        monitor='val_loss',
                        patience=5,
                        restore_best_weights=True
                    )
                ]
            )
            logger.info("Model training completed successfully")
            return history
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """
        Make predictions on the input data
        
        Args:
            input_data: Input features to predict on
            
        Returns:
            Model predictions
        """
        if self.model is None:
            raise ValueError("Model has not been trained or loaded yet!")
            
        try:
            predictions = self.model.predict(input_data)
            return predictions
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise

    def save_model(self, path: str) -> None:
        """
        Save the model to the specified path
        
        Args:
            path: Path to save the model
        """
        if self.model is None:
            raise ValueError("No model to save!")
            
        try:
            self.model.save(path)
            logger.info(f"Model saved successfully to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise

    def load_model(self, path: str) -> None:
        """
        Load a saved model from the specified path
        
        Args:
            path: Path to the saved model
        """
        try:
            self.model = tf.keras.models.load_model(path)
            logger.info(f"Model loaded successfully from {path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Tuple[float, float]:
        """
        Evaluate the model on test data
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Tuple of (loss, accuracy)
        """
        if self.model is None:
            raise ValueError("Model has not been trained or loaded yet!")
            
        try:
            loss, accuracy = self.model.evaluate(X_test, y_test)
            logger.info(f"Model evaluation - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
            return loss, accuracy
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise
