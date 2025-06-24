#!/usr/bin/env python3
"""
ORV Study Buddy - Portable Study Timer with Kim Dokja Animations
Cross-Platform Implementation (Windows/Linux/Raspberry Pi)
"""

import pygame
import time
import json
import os
import threading
from datetime import datetime, timedelta
from enum import Enum
import math
import sys

# Platform detection
try:
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
    print("Running on Raspberry Pi")
except ImportError:
    IS_RASPBERRY_PI = False
    print("Running on desktop - RPi.GPIO not available")

# Hardware Configuration (only used on Raspberry Pi)
if IS_RASPBERRY_PI:
    POWER_BUTTON_PIN = 3
    BUZZER_PIN = 18

# Display dimensions
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240

# Timer Configuration
WORK_SESSION_MINUTES = 25
SHORT_BREAK_MINUTES = 5
LONG_BREAK_MINUTES = 15
SESSIONS_BEFORE_LONG_BREAK = 4

# Colors (ORV themed)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (70, 130, 180)
DARK_BLUE = (25, 25, 112)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (105, 105, 105)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

class TimerState(Enum):
    IDLE = "idle"
    WORKING = "working"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"

class KimDokjaState(Enum):
    IDLE = "idle"
    WORKING = "working"
    RESTING = "resting"
    CELEBRATING = "celebrating"

class ORVStudyBuddy:
    def __init__(self):
        # Initialize GPIO only on Raspberry Pi
        if IS_RASPBERRY_PI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(POWER_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(BUZZER_PIN, GPIO.OUT)
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Set up display
        try:
            self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
            pygame.display.set_caption("ORV Study Buddy")
        except:
            # Fallback for headless systems
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        
        # Initialize fonts
        try:
            self.large_font = pygame.font.Font(None, 36)
            self.medium_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        except:
            # Fallback fonts
            self.large_font = pygame.font.SysFont('arial', 36)
            self.medium_font = pygame.font.SysFont('arial', 24)
            self.small_font = pygame.font.SysFont('arial', 18)
        
        # Timer state
        self.timer_state = TimerState.IDLE
        self.kim_dokja_state = KimDokjaState.IDLE
        self.current_session = 0
        self.sessions_completed = 0
        self.timer_start_time = None
        self.timer_duration = 0
        self.paused_time = 0
        
        # UI state
        self.current_screen = "main"
        self.notes = self.load_notes()
        self.note_input = ""
        self.virtual_keyboard_active = False
        
        # Animation
        self.animation_frame = 0
        self.last_animation_update = time.time()
        
        # Button handling
        self.last_button_press = 0
        self.button_debounce = 0.2
        
        # Setup button interrupt (Raspberry Pi only)
        if IS_RASPBERRY_PI:
            GPIO.add_event_detect(POWER_BUTTON_PIN, GPIO.FALLING, 
                                callback=self.power_button_callback, 
                                bouncetime=200)
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Create data directory (cross-platform)
        if IS_RASPBERRY_PI:
            self.data_dir = '/home/pi/orv_study_data'
        else:
            self.data_dir = os.path.join(os.path.expanduser('~'), 'orv_study_data')
        
        os.makedirs(self.data_dir, exist_ok=True)
        
    def power_button_callback(self, channel):
        """Handle power button press (Raspberry Pi only)"""
        current_time = time.time()
        if current_time - self.last_button_press > self.button_debounce:
            self.last_button_press = current_time
            self.handle_power_button()
    
    def handle_power_button(self):
        """Handle different power button actions based on current state"""
        if self.timer_state == TimerState.IDLE:
            self.start_work_session()
        elif self.timer_state in [TimerState.WORKING, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            if self.timer_state == TimerState.PAUSED:
                self.resume_timer()
            else:
                self.pause_timer()
        elif self.timer_state == TimerState.PAUSED:
            self.resume_timer()
    
    def play_buzzer(self, duration=0.5, frequency=1000):
        """Play buzzer sound (hardware buzzer on RPi, pygame sound on desktop)"""
        if IS_RASPBERRY_PI:
            def buzzer_thread():
                pwm = GPIO.PWM(BUZZER_PIN, frequency)
                pwm.start(50)
                time.sleep(duration)
                pwm.stop()
            
            thread = threading.Thread(target=buzzer_thread)
            thread.daemon = True
            thread.start()
        else:
            # Desktop fallback: generate beep sound with pygame
            try:
                # Generate a simple beep sound
                sample_rate = 22050
                frames = int(duration * sample_rate)
                arr = []
                for i in range(frames):
                    wave = 4096 * math.sin(2 * math.pi * frequency * i / sample_rate)
                    arr.append([int(wave), int(wave)])
                
                sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
                sound.play()
            except:
                # If sound generation fails, just print
                print(f"BEEP! ({frequency}Hz for {duration}s)")
    
    def start_work_session(self):
        """Start a work session"""
        self.timer_state = TimerState.WORKING
        self.kim_dokja_state = KimDokjaState.WORKING
        self.timer_duration = WORK_SESSION_MINUTES * 60
        self.timer_start_time = time.time()
        self.paused_time = 0
        print(f"Started work session {self.sessions_completed + 1}")
    
    def start_break(self, long_break=False):
        """Start break session"""
        if long_break:
            self.timer_state = TimerState.LONG_BREAK
            self.timer_duration = LONG_BREAK_MINUTES * 60
            print("Started long break")
        else:
            self.timer_state = TimerState.SHORT_BREAK
            self.timer_duration = SHORT_BREAK_MINUTES * 60
            print("Started short break")
        
        self.kim_dokja_state = KimDokjaState.RESTING
        self.timer_start_time = time.time()
        self.paused_time = 0
    
    def pause_timer(self):
        """Pause the current timer"""
        if self.timer_state != TimerState.IDLE:
            self.timer_state = TimerState.PAUSED
            self.paused_time = time.time() - self.timer_start_time
            print("Timer paused")
    
    def resume_timer(self):
        """Resume the paused timer"""
        if self.timer_state == TimerState.PAUSED:
            if self.kim_dokja_state == KimDokjaState.WORKING:
                self.timer_state = TimerState.WORKING
            elif self.kim_dokja_state == KimDokjaState.RESTING:
                if self.sessions_completed % SESSIONS_BEFORE_LONG_BREAK == 0 and self.sessions_completed > 0:
                    self.timer_state = TimerState.LONG_BREAK
                else:
                    self.timer_state = TimerState.SHORT_BREAK
            
            self.timer_start_time = time.time() - self.paused_time
            print("Timer resumed")
    
    def check_timer(self):
        """Check timer status and handle completions"""
        if self.timer_state in [TimerState.WORKING, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            elapsed = time.time() - self.timer_start_time
            if elapsed >= self.timer_duration:
                self.timer_complete()
    
    def timer_complete(self):
        """Handle timer completion"""
        self.play_buzzer(duration=1.0, frequency=800)
        
        if self.timer_state == TimerState.WORKING:
            self.sessions_completed += 1
            self.kim_dokja_state = KimDokjaState.CELEBRATING
            
            self.save_session_data()
            
            if self.sessions_completed % SESSIONS_BEFORE_LONG_BREAK == 0:
                self.start_break(long_break=True)
            else:
                self.start_break(long_break=False)
        else:
            self.timer_state = TimerState.IDLE
            self.kim_dokja_state = KimDokjaState.IDLE
            print("Break finished - ready for next session")
    
    def get_remaining_time(self):
        """Get remaining time in current timer"""
        if self.timer_state == TimerState.PAUSED:
            return self.timer_duration - self.paused_time
        elif self.timer_state in [TimerState.WORKING, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            elapsed = time.time() - self.timer_start_time
            return max(0, self.timer_duration - elapsed)
        return 0
    
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def draw_kim_dokja(self, x, y, size=60):
        """Draw Kim Dokja character with static sprite support"""
        sprite_name = self._get_sprite_name()
        
        if self._draw_sprite(sprite_name, x, y, size):
            self._add_sprite_effects(x, y, size)
            return
        
        frame = (pygame.time.get_ticks() // 100) % 8
        self._draw_simple_animated_character(x, y, size, frame)

    def _get_sprite_name(self):
        """Generate sprite filename based on current state"""
        state_names = {
            KimDokjaState.IDLE: "idle",
            KimDokjaState.WORKING: "idle",
            KimDokjaState.RESTING: "idle",
            KimDokjaState.CELEBRATING: "idle"
        }
        
        state = state_names.get(self.kim_dokja_state, "idle")
        return f"kim_dokja_{state}.png"

    def _add_sprite_effects(self, x, y, size):
        """Add subtle animation effects to static sprites"""
        frame = (pygame.time.get_ticks() // 100) % 60
        
        float_offset = int(3 * math.sin(frame * 0.1))
        
        if self.kim_dokja_state == KimDokjaState.WORKING:
            book_x = x + size//3
            book_y = y - size//3 + float_offset
            pygame.draw.rect(self.screen, BLUE, (book_x, book_y, 12, 8))
            pygame.draw.rect(self.screen, BLACK, (book_x, book_y, 12, 8), 1)
            
        elif self.kim_dokja_state == KimDokjaState.RESTING:
            if frame % 40 < 30:
                font_small = pygame.font.Font(None, 20)
                zzz_text = font_small.render("z", True, (100, 100, 100))
                zzz_x = x + size//3 + int(2 * math.sin(frame * 0.2))
                zzz_y = y - size//2 + float_offset
                self.screen.blit(zzz_text, (zzz_x, zzz_y))
                
        elif self.kim_dokja_state == KimDokjaState.CELEBRATING:
            import random
            random.seed(frame)
            for i in range(3):
                sparkle_x = x + random.randint(-size//2, size//2)
                sparkle_y = y + random.randint(-size//2, size//2) + float_offset
                sparkle_size = random.randint(2, 4)
                pygame.draw.circle(self.screen, YELLOW, (sparkle_x, sparkle_y), sparkle_size)

    def _draw_sprite(self, sprite_name, x, y, size):
        """Try to load and draw sprite image"""
        try:
            sprite_path = f"assets/characters/{sprite_name}"
            
            if not hasattr(self, '_sprite_cache'):
                self._sprite_cache = {}
                
            if sprite_name not in self._sprite_cache:
                sprite = pygame.image.load(sprite_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (size, size))
                self._sprite_cache[sprite_name] = sprite
            
            sprite = self._sprite_cache[sprite_name]
            sprite_rect = sprite.get_rect(center=(x, y))
            self.screen.blit(sprite, sprite_rect)
            return True
            
        except (pygame.error, FileNotFoundError):
            return False

    def _draw_simple_animated_character(self, x, y, size, frame):
        """Enhanced fallback drawing with better animation"""
        colors = {
            KimDokjaState.IDLE: WHITE,
            KimDokjaState.WORKING: BLUE,
            KimDokjaState.RESTING: GREEN,
            KimDokjaState.CELEBRATING: ORANGE
        }
        color = colors.get(self.kim_dokja_state, WHITE)
        
        breath_offset = int(2 * math.sin(frame * 0.5))
        char_y = y + breath_offset
        
        pygame.draw.circle(self.screen, color, (x, char_y), size//2)
        pygame.draw.circle(self.screen, BLACK, (x, char_y), size//2, 2)
        
        eye_y = char_y - size//6
        eye_size = 3
        
        if frame % 60 < 3:
            pygame.draw.line(self.screen, BLACK, 
                            (x-size//6-2, eye_y), (x-size//6+2, eye_y), 2)
            pygame.draw.line(self.screen, BLACK, 
                            (x+size//6-2, eye_y), (x+size//6+2, eye_y), 2)
        else:
            pygame.draw.circle(self.screen, BLACK, (x-size//6, eye_y), eye_size)
            pygame.draw.circle(self.screen, BLACK, (x+size//6, eye_y), eye_size)
        
        mouth_y = char_y + size//6
        
        if self.kim_dokja_state == KimDokjaState.CELEBRATING:
            bounce = int(2 * math.sin(frame * 0.8))
            pygame.draw.arc(self.screen, BLACK, 
                           (x-size//4, mouth_y-5+bounce, size//2, 10), 
                           0, math.pi, 3)
        elif self.kim_dokja_state == KimDokjaState.WORKING:
            pygame.draw.line(self.screen, BLACK, 
                            (x-size//8, mouth_y), (x+size//8, mouth_y), 2)
            pygame.draw.rect(self.screen, BLUE, (x+size//3, char_y-5, 8, 6))
        elif self.kim_dokja_state == KimDokjaState.RESTING:
            mouth_width = 6 + int(2 * math.sin(frame * 0.3))
            pygame.draw.ellipse(self.screen, BLACK, 
                               (x-mouth_width//2, mouth_y-2, mouth_width, 4))
            if frame % 30 < 20:
                font_small = pygame.font.Font(None, 16)
                zzz_text = font_small.render("z", True, BLACK)
                self.screen.blit(zzz_text, (x+size//3, char_y-size//3))
        else:
            pygame.draw.circle(self.screen, BLACK, (x, mouth_y), 2)
    
    def draw_main_screen(self):
        """Draw the main timer screen"""
        self.screen.fill(BLACK)
        
        title_text = self.large_font.render("ORV Study Buddy", True, WHITE)
        title_rect = title_text.get_rect(center=(DISPLAY_WIDTH//2, 30))
        self.screen.blit(title_text, title_rect)
        
        self.draw_kim_dokja(DISPLAY_WIDTH//2, 100)
        
        remaining_time = self.get_remaining_time()
        time_text = self.large_font.render(self.format_time(remaining_time), True, WHITE)
        time_rect = time_text.get_rect(center=(DISPLAY_WIDTH//2, 150))
        self.screen.blit(time_text, time_rect)
        
        status_text = ""
        if self.timer_state == TimerState.IDLE:
            status_text = "Press SPACE to start!" if not IS_RASPBERRY_PI else "Press button to start!"
        elif self.timer_state == TimerState.WORKING:
            status_text = f"Work Session {self.sessions_completed + 1}"
        elif self.timer_state == TimerState.SHORT_BREAK:
            status_text = "Short Break"
        elif self.timer_state == TimerState.LONG_BREAK:
            status_text = "Long Break"
        elif self.timer_state == TimerState.PAUSED:
            status_text = "Paused - Press SPACE to resume" if not IS_RASPBERRY_PI else "Paused - Press to resume"
        
        status_surface = self.medium_font.render(status_text, True, WHITE)
        status_rect = status_surface.get_rect(center=(DISPLAY_WIDTH//2, 180))
        self.screen.blit(status_surface, status_rect)
        
        session_text = f"Sessions completed: {self.sessions_completed}"
        session_surface = self.small_font.render(session_text, True, WHITE)
        session_rect = session_surface.get_rect(center=(DISPLAY_WIDTH//2, 200))
        self.screen.blit(session_surface, session_rect)
        
        pygame.draw.rect(self.screen, DARK_BLUE, (10, 210, 60, 25))
        notes_text = self.small_font.render("Notes", True, WHITE)
        self.screen.blit(notes_text, (15, 215))
        
        pygame.draw.rect(self.screen, DARK_BLUE, (250, 210, 60, 25))
        stats_text = self.small_font.render("Stats", True, WHITE)
        self.screen.blit(stats_text, (255, 215))
    
    def draw_notes_screen(self):
        """Draw the notes screen"""
        self.screen.fill(BLACK)
        
        title_text = self.medium_font.render("Notes", True, WHITE)
        self.screen.blit(title_text, (10, 10))
        
        pygame.draw.rect(self.screen, DARK_BLUE, (250, 5, 60, 25))
        back_text = self.small_font.render("Back", True, WHITE)
        self.screen.blit(back_text, (270, 10))
        
        y_offset = 40
        for i, note in enumerate(self.notes[-8:]):
            note_text = self.small_font.render(f"{i+1}. {note[:40]}", True, WHITE)
            self.screen.blit(note_text, (10, y_offset))
            y_offset += 20
        
        pygame.draw.rect(self.screen, GREEN, (10, 200, 100, 30))
        add_text = self.small_font.render("Add Note", True, WHITE)
        self.screen.blit(add_text, (25, 210))
        
        if self.virtual_keyboard_active:
            pygame.draw.rect(self.screen, DARK_GRAY, (120, 200, 190, 30))
            input_text = self.small_font.render(self.note_input[-25:], True, WHITE)
            self.screen.blit(input_text, (125, 210))
    
    def handle_touch(self, pos):
        """Handle touch screen input"""
        x, y = pos
        
        if self.current_screen == "main":
            if 10 <= x <= 70 and 210 <= y <= 235:
                self.current_screen = "notes"
            elif 250 <= x <= 310 and 210 <= y <= 235:
                self.show_stats()
        
        elif self.current_screen == "notes":
            if 250 <= x <= 310 and 5 <= y <= 30:
                self.current_screen = "main"
            elif 10 <= x <= 110 and 200 <= y <= 230:
                self.virtual_keyboard_active = True
                self.note_input = ""
    
    def show_stats(self):
        """Show session statistics"""
        total_time = self.sessions_completed * WORK_SESSION_MINUTES
        print(f"Total study time: {total_time} minutes")
        print(f"Sessions completed: {self.sessions_completed}")
    
    def load_notes(self):
        """Load notes from file"""
        try:
            with open(os.path.join(self.data_dir, 'notes.json'), 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_notes(self):
        """Save notes to file"""
        try:
            with open(os.path.join(self.data_dir, 'notes.json'), 'w') as f:
                json.dump(self.notes, f)
        except Exception as e:
            print(f"Error saving notes: {e}")
    
    def save_session_data(self):
        """Save session completion data"""
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'session_number': self.sessions_completed,
            'duration_minutes': WORK_SESSION_MINUTES
        }
        
        try:
            sessions = []
            try:
                with open(os.path.join(self.data_dir, 'sessions.json'), 'r') as f:
                    sessions = json.load(f)
            except:
                pass
            
            sessions.append(session_data)
            
            with open(os.path.join(self.data_dir, 'sessions.json'), 'w') as f:
                json.dump(sessions, f)
        except Exception as e:
            print(f"Error saving session data: {e}")
    
    def update_animation(self):
        """Update character animation"""
        current_time = time.time()
        if current_time - self.last_animation_update > 0.5:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.last_animation_update = current_time
    
    def run(self):
        """Main application loop"""
        running = True
        
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_touch(event.pos)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE and not IS_RASPBERRY_PI:
                            # Space bar acts as power button on desktop
                            self.handle_power_button()
                        elif self.virtual_keyboard_active:
                            if event.key == pygame.K_RETURN:
                                if self.note_input.strip():
                                    self.notes.append(self.note_input.strip())
                                    self.save_notes()
                                self.virtual_keyboard_active = False
                                self.note_input = ""
                            elif event.key == pygame.K_BACKSPACE:
                                self.note_input = self.note_input[:-1]
                            else:
                                if len(self.note_input) < 100:
                                    self.note_input += event.unicode
                
                self.check_timer()
                self.update_animation()
                
                if self.current_screen == "main":
                    self.draw_main_screen()
                elif self.current_screen == "notes":
                    self.draw_notes_screen()
                
                pygame.display.flip()
                self.clock.tick(30)
                
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if IS_RASPBERRY_PI:
            GPIO.cleanup()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("Starting ORV Study Buddy...")
    app = ORVStudyBuddy()
    app.run()