import pygame # For graphics
import sys # Sys operations like exit
import json # Handle json data and transforms into utf-8 encoding in a function for minimum data
import os # Filepath operations
import random # Any rng aspect
import textwrap # Life saver for text display :pray:
import math # Anim calculations mainly

# Pygame mixer
pygame.mixer.init()
pygame.init()

# App icon
try:
    icon_image = pygame.image.load("Meshes\\logo.png")
    pygame.display.set_icon(icon_image)
except Exception as e:
    print(f"Logo load error: {e}")

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BUTTON_COLOR = (50, 50, 150)
TEXT_COLOR = (255, 255, 255)
BUTTON_HOVER_COLOR = (80, 80, 180)
PROGRESS_BAR_COLOR = (0, 0, 255)
COPYRIGHT_TEXT = "© Educa College Prep - All Rights of 'sat_data' Reserved, more info on readme"
DATA_DIR = "sat_data"

# List of current subjects
SUBJECT_PARTS = [
    'geometry1', 'geometry2', 'geometry3', 'statistics1',
    'arithmetic1', 'arithmetic2', 'algebra1', 'algebra2',
    'algebra3', 'algebra4', 'functions1'
]

# Motivational speeches :D
MOTIVATIONAL_SPEECHES = [
    "Keep going!",
    "You're unstoppable!",
    "You're on fire!",
    "Crushing it!",
    "You're a genius!",
    "Rock on!",
    "You're killing it!",
    "Way to go!",
    "You're a star!",
    "Incredible job!",
    "Boom, nailed it!",
    "You're a champ!",
    "Fantastic work!",
    "You're on a roll!",
    "Superb effort!",
    "You're a legend!",
    "Amazing job!",
    "You're soaring!",
    "Top-notch work!",
    "You're unstoppable!",
    "Brilliant move!",
    "You're a hero!",
    "Outstanding effort!",
    "You're a rockstar!",
    "Epic win!",
    "You're a pro!",
    "Stellar performance!",
    "You're crushing goals!",
    "Phenomenal work!",
    "You're the best!"
]


MULTI_CHOICE_VARIATIONS = [
    "multi_choice", "multiple choice", "multi choice", "multichoice", "multiplechoice",
    "mcq", "multiple choice question", "multi-choice", "multiple-choice",
    "Multi-Choice"  # Add the exact JSON form
]


FILL_IN_VARIATIONS = [
    "fill_in", "fill in", "fill-ins", "fillins", "fill in blank", "fill-in",
    "fill in blanks", "Fill-in"  # Add the exact JSON form
]

# Load icons with fallback in 36 x 36
if not os.path.exists('Meshes/folder_icon.png'):
    print("Warning: Missing folder_icon.png")
    FOLDER_ICON = pygame.Surface((36, 36)) # Placeholder to scale
    FOLDER_ICON.fill(GRAY)
else:
    FOLDER_ICON = pygame.image.load('Meshes/folder_icon.png')
    FOLDER_ICON = pygame.transform.scale(FOLDER_ICON, (36, 36)) # Scaling

if not os.path.exists('Meshes/drive.png'):
    print("Warning: Missing drive.png")
    DRIVE_ICON = pygame.Surface((36, 36)) 
    DRIVE_ICON.fill(GRAY)
else:
    DRIVE_ICON = pygame.image.load('Meshes/drive.png')
    DRIVE_ICON = pygame.transform.scale(DRIVE_ICON, (36, 36))

if not os.path.exists('Meshes/trophy.png'):
    print("Warning: Missing trophy.png")
    TROPHY_ICON = pygame.Surface((36, 36))
    TROPHY_ICON.fill(GRAY)
else:
    TROPHY_ICON = pygame.image.load('Meshes/trophy.png')
    TROPHY_ICON = pygame.transform.scale(TROPHY_ICON, (36, 36))

# Volume and animation settings
VOLUMES = {'click': 1.0, 'correct': 1.0, 'incorrect': 1.0}
ANIMATION_DURATION = 2000 
SUBMIT_COOLDOWN = 5000  # 5 sec in milliseconds
 #                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 # BEWARE THAT BY CHANGING THESE CONSTANTS THE CODE MAY BREAK

# Sound initialization with error handling
try:
    SOUND_BUTTON_CLICK = pygame.mixer.Sound('Sounds/click.wav')
    SOUND_CORRECT = pygame.mixer.Sound('Sounds/correct.wav')
    SOUND_INCORRECT = pygame.mixer.Sound('Sounds/incorrect.wav')
    SOUND_PAPER_FOLD = pygame.mixer.Sound('Sounds/paper_fold.wav')
except Exception as e:
    print(f"Sound error: {e}")
    SOUND_BUTTON_CLICK = pygame.mixer.Sound(buffer=b'')
    SOUND_CORRECT = pygame.mixer.Sound(buffer=b'')
    SOUND_INCORRECT = pygame.mixer.Sound(buffer=b'')
    SOUND_PAPER_FOLD = pygame.mixer.Sound(buffer=b'')

SOUND_BUTTON_CLICK.set_volume(VOLUMES['click'])
SOUND_CORRECT.set_volume(VOLUMES['correct'])
SOUND_INCORRECT.set_volume(VOLUMES['incorrect'])
SOUND_PAPER_FOLD.set_volume(VOLUMES['click'])

# Setup display, font, and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SAT Study Helper")
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
clock = pygame.time.Clock()

# Utility function to safely play sounds
def play_safe(sound):
    try:
        sound.play()
    except Exception as e:
        print(f"Sound play error: {e}")

def draw_wrapped_text(surface, text, x, y, font, color, max_width):
    wrapped_lines = textwrap.wrap(text, width=max_width // font.size(" ")[0])
    y_offset = 0
    for line in wrapped_lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + y_offset))
        y_offset += font.get_height()

def draw_loading_screen(screen, message):
    """Display a loading screen with a custom message."""
    screen.fill(BLACK)
    draw_wrapped_text(screen, message, SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2, font, WHITE, 600)
    pygame.display.flip()

# Initialize JSON files if missing or invalid
def initialize_json_files():
    """Initialize JSON files for each subject part if missing or empty."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)  # Create directory if it doesn’t exist
    for part in SUBJECT_PARTS:
        filepath = os.path.join(DATA_DIR, f"{part}.json")
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            default_data = {
                "sections": {
                    "sectionA": {"section_name": "Section A", "questions": [], "aced_questions": []},
                    "sectionB": {"section_name": "Section B", "questions": [], "aced_questions": []}
                }
            }
            if part == "arithmetic1":  # Match example JSON structure
                default_data["sections"]["sectionC"] = {"section_name": "Section C", "questions": [], "aced_questions": []}
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)
                print(f"Initialized {filepath} with default data")

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content or content in ['{}', '[]']:
                print(f"{filepath} is empty or minimal, returning default")
                return {"sections": {}}
            data = json.loads(content)
            # Print the "Loaded" message first
            print(f"Loaded {filepath}:")
            # Print the full JSON data with indentation
            print(json.dumps(data, indent=2))
            return data
    except json.JSONDecodeError as e:
        print(f"Error loading {filepath}: Invalid JSON format - {str(e)}")
        return {"sections": {}}
    except FileNotFoundError:
        print(f"Warning: {filepath} not found. Returning default structure.")
        return {"sections": {}}

class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.parent = None
        self.max_width = width - 10  # Account for padding

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.parent:
                    self.parent.check_answer()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Only add character if it fits
                temp_text = self.text + event.unicode
                if font.size(temp_text)[0] <= self.max_width:
                    self.text = temp_text

    def draw(self, screen):
        border_color = (0, 0, 255) if self.active else (0, 0, 0)  
        pygame.draw.rect(screen, (255, 255, 255), self.rect)  
        pygame.draw.rect(screen, border_color, self.rect, 2)
        text_surf = font.render(self.text, True, (0, 0, 0)) 
        if text_surf.get_width() > self.max_width:
            for i in range(len(self.text), -1, -1):
                clipped_text = self.text[:i]
                if font.size(clipped_text)[0] <= self.max_width:
                    text_surf = font.render(clipped_text, True, (0, 0, 0))
                    break
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

# Utility functions
class ProgressBar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_progress = 0  
        self.target_progress = 0   
        self.start_time = None
        self.animation_duration = 1000 
        self.animation_active = False

    def start_animation(self, target_progress):
        """Start animating to the target progress."""
        self.start_time = pygame.time.get_ticks()
        self.target_progress = max(0, min(1, target_progress))  # Clamp between 0 and 1
        self.animation_active = True

    def update(self, progress_percentage=None):
        """Update the progress bar animation."""
        if progress_percentage is not None and not self.animation_active:
            self.start_animation(progress_percentage)
        if self.animation_active:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            if elapsed < self.animation_duration:
                t = elapsed / self.animation_duration
                # Use smoothstep for a natural animation curve
                t = t * t * (3 - 2 * t)
                self.current_progress = self.current_progress + (self.target_progress - self.current_progress) * t
            else:
                self.current_progress = self.target_progress
                self.animation_active = False

    def draw(self, surface):
        """Draw the progress bar."""
        # Background
        pygame.draw.rect(surface, GRAY, (self.x, self.y, self.width, self.height))
        # Animated fill
        fill_width = int(self.width * self.current_progress)
        pygame.draw.rect(surface, PROGRESS_BAR_COLOR, (self.x, self.y, fill_width, self.height))

# Answer Animation class
class AnswerAnimation:
    def __init__(self):
        self.start_time = 0
        self.message = ""
        self.y_pos = SCREEN_HEIGHT

    def start(self, is_correct):
        self.start_time = pygame.time.get_ticks()
        self.message = "Correct! :)" if is_correct else "Incorrect :("
        self.y_pos = SCREEN_HEIGHT

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        if 0 < elapsed < ANIMATION_DURATION + 500:
            if elapsed < ANIMATION_DURATION:
                progress = min(elapsed / ANIMATION_DURATION, 1.0)
                self.y_pos = SCREEN_HEIGHT - int(100 * math.sin(progress * math.pi/2))
            else:
                self.y_pos += 5
        else:
            self.y_pos = SCREEN_HEIGHT + 100

    def draw_animation(self, screen):
        color = (0, 255, 0) if "Correct" in self.message else (255, 0, 0)
        text_surf = font.render(f"{self.message}", True, color)
        screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, self.y_pos))

# SolutionSheet class with scrolling and improved scaling
class SolutionSheet:
    def __init__(self):
        self.preview_active = False
        self.opened = False
        self.sheet_image = None
        self.real_answer_sheet = None
        self.preview_width = 290
        self.preview_height = 290
        self.full_width = 500  
        self.full_height = SCREEN_HEIGHT - 100 
        self.preview_x = SCREEN_WIDTH - self.preview_width - 90
        self.preview_y = 200
        self.x = self.preview_x
        self.y = self.preview_y
        self.width = self.preview_width
        self.height = self.preview_height
        self.hovered = False
        self.close_rect = None
        self.close_hovered = False
        self.scroll_y = 0  # Scroll position
        self.image_height = 0  # Full height of the scaled image

    def start_preview(self, sheet_path, real_path=None):
        try:
            self.sheet_image = pygame.image.load(sheet_path).convert_alpha()
            self.sheet_image = pygame.transform.scale(self.sheet_image, (self.preview_width, self.preview_height))
            self.real_answer_sheet = real_path
            self.preview_active = True
            self.opened = False
            self.x = self.preview_x
            self.y = self.preview_y
            self.width = self.preview_width
            self.height = self.preview_height
            self.scroll_y = 0
        except Exception as e:
            print(f"Error loading solution sheet: {e}")
            self.preview_active = False

    def update(self):
        current_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = not self.opened and current_rect.collidepoint(mouse_pos)
        if self.opened and self.close_rect:
            self.close_hovered = self.close_rect.collidepoint(mouse_pos)

    def toggle_open(self):
        if self.preview_active:
            if not self.opened and self.real_answer_sheet:
                try:
                    # Load the real answer sheet image
                    original_image = pygame.image.load(self.real_answer_sheet).convert_alpha()
                    # Calculate aspect ratio and scale to fixed width, preserving height
                    orig_width, orig_height = original_image.get_size()
                    aspect_ratio = orig_height / orig_width
                    self.image_height = int(self.full_width * aspect_ratio)
                    self.sheet_image = pygame.transform.scale(original_image, (self.full_width, self.image_height))
                    # Set viewport dimensions
                    self.width = self.full_width
                    self.height = self.full_height
                    self.x = SCREEN_WIDTH - self.full_width - 225
                    self.y = 50  # Top of the screen with some padding
                    self.opened = True
                    self.scroll_y = 0  # Reset scroll position
                except Exception as e:
                    print(f"Error loading real answer sheet: {e}")
                    self.sheet_image = pygame.Surface((self.full_width, self.image_height), pygame.SRCALPHA)
                    self.sheet_image.fill((0, 0, 0, 0))
                    self.width = self.full_width
                    self.height = self.full_height
                    self.x = SCREEN_WIDTH - self.full_width - 225
                    self.y = 50
                    self.opened = True
                    self.scroll_y = 0
            else:
                try:
                    # Reset to preview mode
                    self.sheet_image = pygame.image.load("Meshes/answer_sheet.png").convert_alpha()
                    self.sheet_image = pygame.transform.scale(self.sheet_image, (self.preview_width, self.preview_height))
                except Exception as e:
                    print(f"Error resetting to preview: {e}")
                    self.sheet_image = pygame.Surface((self.preview_width, self.preview_height), pygame.SRCALPHA)
                self.width = self.preview_width
                self.height = self.preview_height
                self.x = self.preview_x
                self.y = self.preview_y
                self.opened = False
                self.scroll_y = 0
            play_safe(SOUND_PAPER_FOLD)

    def handle_event(self, event, quiz_screen):
        if event is None:  # Prevent NoneType errors
            return
    # Restrict to left mouse button only (event.button == 1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.preview_active:
            mouse_pos = event.pos
            current_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if self.opened and self.close_rect and self.close_rect.collidepoint(mouse_pos):
                self.toggle_open()
            elif not self.opened and current_rect.collidepoint(mouse_pos):
                self.toggle_open()
                if quiz_screen.state.current_question and "answer_sheet" in quiz_screen.state.current_question:
                    self.real_answer_sheet = quiz_screen.state.current_question['answer_sheet']
        elif event.type == pygame.MOUSEWHEEL and self.opened:
        # Scroll wheel only adjusts scroll position
            scroll_amount = -event.y * 30
            self.scroll_y = max(0, min(self.scroll_y + scroll_amount, max(0, self.image_height - self.height)))

    def draw(self, screen):
        if not self.preview_active:
            return
        self.update()
        current_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if self.opened:
            src_rect = pygame.Rect(0, self.scroll_y, self.full_width, min(self.height, self.image_height - self.scroll_y))
            dest_rect = pygame.Rect(self.x, self.y, self.width, min(self.height, self.image_height - self.scroll_y))
            screen.blit(self.sheet_image, dest_rect, src_rect)
            # Draw close button
            self.close_rect = pygame.Rect(self.x + self.width - 40, self.y - 40, 30, 30)
            close_color = (200, 0, 0) if self.close_hovered else (255, 0, 0)
            pygame.draw.rect(screen, close_color, self.close_rect)
            pygame.draw.line(screen, WHITE,
                             (self.close_rect.x + 5, self.close_rect.y + 5),
                             (self.close_rect.x + 25, self.close_rect.y + 25), 2)
            pygame.draw.line(screen, WHITE,
                             (self.close_rect.x + 25, self.close_rect.y + 5),
                             (self.close_rect.x + 5, self.close_rect.y + 25), 2)
            # Add scroll message if scrollable
            if self.image_height > self.height:
                scroll_text = font.render("Scroll to view the full answer sheet", True, BLACK)
                screen.blit(scroll_text, (self.x + self.width -460, self.y -30))
        else:
            color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
            pygame.draw.rect(screen, color, current_rect)
            screen.blit(self.sheet_image, current_rect)
            answer_sheet_text = large_font.render("Answer Sheet", True, BLACK)
            screen.blit(answer_sheet_text, (current_rect.x, current_rect.bottom + 10))


# Button class with icon support and dynamic width adjustment
class Button:
    def __init__(self, x, y, width, height, text, callback, disabled=False, icon=None, parent=None):
        self.x = x
        self.y = y
        self.min_width = width
        self.min_height = height
        self.text = text
        self.callback = callback
        self.disabled = disabled
        self.icon = icon
        self.parent = parent
        self.hovered = False
        
        # Calculate width with proper padding
        if self.icon:
            wrap_width = (self.min_width - 56 - 20) // font.size(" ")[0]  # 56 = 10 + 36 + 10, 20 = right padding
        else:
            wrap_width = (self.min_width - 20) // font.size(" ")[0]  # 10 left + 10 right padding
        self.lines = textwrap.wrap(text, width=wrap_width)
        text_width = max([font.size(line)[0] for line in self.lines], default=0)
        if self.icon:
            self.width = max(self.min_width, 56 + text_width + 20)  # Icon space + text + right padding
        else:
            self.width = max(self.min_width, 10 + text_width + 10)  # Left + text + right padding
        self.height = max(self.min_height, len(self.lines) * font.get_height() + 20)
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update_hover(self, mouse_pos):
        """Update the hover state based on mouse position."""
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Render the button on the screen."""
        if self.disabled:
            color = GRAY
        elif self.hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        # Draw icon if present
        if self.icon:
            screen.blit(self.icon, (self.x + 10, self.y + (self.height - self.icon.get_height()) // 2))
        # Draw text
        text_x = self.x + (56 if self.icon else 10)
        text_y = self.y + 10
        for line in self.lines:
            text_surf = font.render(line, True, TEXT_COLOR)
            screen.blit(text_surf, (text_x, text_y))
            text_y += font.get_height()

    def handle_event(self, event):
        """Handle mouse events for the button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and not self.disabled:
                self.callback()
                play_safe(SOUND_BUTTON_CLICK)

# Slider class for aced questions navigation
class Slider:
    def __init__(self, x, y, width, height, min_value, max_value):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value if max_value > min_value else min_value + 1
        self.value = min_value
        self.dragging = False
        self.handle_width = 20
        self.handle_height = height * 2

    def update(self, mouse_pos, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
                self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                relative_x = mouse_pos[0] - self.rect.x
                if self.rect.width > 0:
                    self.value = self.min_value + (self.max_value - self.min_value) * (relative_x / self.rect.width)
                    self.value = max(self.min_value, min(self.max_value, round(self.value)))

    def draw(self, screen):
        if self.max_value == self.min_value:
            handle_x = self.rect.x
            handle_rect = pygame.Rect(handle_x, self.rect.y - (self.handle_height - self.rect.height) / 2, self.handle_width, self.handle_height)
            pygame.draw.rect(screen, BUTTON_COLOR, handle_rect)
        else:
            pygame.draw.rect(screen, GRAY, self.rect)
            if self.rect.width > 0:
                handle_x = self.rect.x + (self.value - self.min_value) * (self.rect.width - self.handle_width) / (self.max_value - self.min_value)
                handle_rect = pygame.Rect(handle_x, self.rect.y - (self.handle_height - self.rect.height) / 2, self.handle_width, self.handle_height)
                pygame.draw.rect(screen, BUTTON_COLOR, handle_rect)

# GameState class with integrated load_questions and save_questions
class GameState:
    def __init__(self):
        self.current_screen = "main_menu"
        self.all_data = {}
        self.current_part = None
        self.current_sections = []
        self.current_session = {'remaining': [], 'total_questions': 0, 'aced_in_session': set(), 'solved': set()}
        self.current_question = None
        self.tries_left = 3
        self.show_answer = False
        self.randomize = False
        self.last_submit_time = 0
        self.quiz_start_time = 0
        self.current_question_index = 0
        self.aced_questions = {part: {} for part in SUBJECT_PARTS}
        self.main_menu_confirmation = False
        self.reset_timer_confirmation = False

    def can_submit(self):
        return pygame.time.get_ticks() - self.last_submit_time >= SUBMIT_COOLDOWN

    def start_new_session(self, subject_part, sections):
        self.current_part = subject_part
        self.current_sections = sections
        self.current_session = {'remaining': [], 'total_questions': 0, 'aced_in_session': set(), 'solved': set()}
        all_questions = []
        for section in sections:
            questions = self.load_questions(subject_part, section)  # Load dynamically here
            aced_ids = {aq['id'] for aq in self.aced_questions[subject_part].get(section, [])}
            section_questions = [q for q in questions if q['id'] not in aced_ids]
            all_questions.extend(section_questions)
        if not all_questions:
            self.current_screen = "main_menu"
            return
        self.current_session['remaining'] = all_questions
        if self.randomize:
            random.shuffle(self.current_session['remaining'])
        self.current_session['total_questions'] = len(self.current_session['remaining']) + sum(len(self.aced_questions[subject_part].get(section, [])) for section in sections)
        self.current_screen = "quiz"
        self.current_question_index = 0
        self.current_question = self.current_session['remaining'][0] if self.current_session['remaining'] else None
        self.quiz_start_time = pygame.time.get_ticks()
        self.last_submit_time = 0
        self.tries_left = 3
        # Calculate initial progress and animate
        initial_aced = self.current_session['total_questions'] - len(self.current_session['remaining'])
        progress = initial_aced / self.current_session['total_questions'] if self.current_session['total_questions'] > 0 else 0
        self.quiz.progress_bar.current_progress = 0  # Reset to 0
        self.quiz.progress_bar.start_animation(progress)  # Animate to initial progress

    def ace_question(self):
        print(f"Acing question {self.current_question['id']}")  # Debug with ID
        if not self.current_question or not self.current_session['remaining']:
            print("No current question or remaining questions to ace")
            return
        question_id = self.current_question['id']
        # Check if already aced globally, not just in session
        already_aced_globally = any(q['id'] == question_id for section in self.current_sections
                                    for q in self.aced_questions[self.current_part].get(section, []))
        if already_aced_globally:
            print(f"Question {question_id} already aced globally, skipping")
            self.quiz.ace_button = None
            return
        if question_id in self.current_session['aced_in_session']:
            print(f"Question {question_id} already aced in this session, skipping")
            self.quiz.ace_button = None
            return
        for section in self.current_sections:
            questions = self.load_questions(self.current_part, section)
            if any(q['id'] == question_id for q in questions):
                print(f"Saving question {question_id} as aced in section {section}")
                self.save_aced_question(self.current_part, section, self.current_question.copy())
                self.current_session['remaining'] = [q for q in self.current_session['remaining'] if q['id'] != question_id]
                self.current_session['aced_in_session'].add(question_id)
                # Update progress bar with animation
                initial_total = self.current_session['total_questions']
                current_remaining = len(self.current_session['remaining'])
                aced_count = initial_total - current_remaining
                progress = aced_count / initial_total if initial_total > 0 else 0
                self.quiz.progress_bar.start_animation(progress)
                if not self.current_session['remaining']:
                    self.show_completion_message()
                    self.current_screen = "main_menu"
                else:
                    self.current_question_index = min(self.current_question_index, len(self.current_session['remaining']) - 1)
                    self.current_question = self.current_session['remaining'][self.current_question_index] if self.current_session['remaining'] else None
                self.quiz.ace_button = None  # Clear ace button after acing
                self.tries_left = 3  # Reset tries after acing
                print(f"Question {question_id} aced successfully. Remaining questions: {len(self.current_session['remaining'])}")
                break

    def show_completion_message(self):
        screen.fill(WHITE)
        text = large_font.render("All questions aced in this section, congrats!", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.current_screen = "main_menu"
        self.current_question = None
        self.current_session.clear()

    def load_aced_questions(self):
        for part in SUBJECT_PARTS:
            data = load_json(os.path.join(DATA_DIR, f"{part}.json"))
            sections = data.get("sections", {})
            for section in sections:
                self.aced_questions[part][section] = sections[section].get('aced_questions', [])

    def save_aced_question(self, part, section, question):
        if 'id' not in question:
            print("Error: Question lacks 'id' field")
            return

        data = load_json(os.path.join(DATA_DIR, f"{part}.json"))
        sections = data.get("sections", {})

        if section not in sections:
            sections[section] = {"section_name": section, "questions": [], "aced_questions": []}

        if 'aced_questions' not in sections[section]:
            sections[section]['aced_questions'] = []

        if not any(q['id'] == question['id'] for q in sections[section]['aced_questions']):
            sections[section]['aced_questions'].append(question)
            self.aced_questions[part][section] = sections[section]['aced_questions']  # Sync in-memory state
            print(f"Saved question {question['id']} to aced_questions in {part}/{section}. Total aced: {len(sections[section]['aced_questions'])}")

        self.save_questions(part, data)

    def unace_question(self, part, section, question_id):
        data = load_json(os.path.join(DATA_DIR, f"{part}.json"))
        sections = data.get("sections", {})

        if section in sections and 'aced_questions' in sections[section]:
            sections[section]['aced_questions'] = [q for q in sections[section]['aced_questions']
                                                  if q['id'] != question_id]
            self.aced_questions[part][section] = sections[section]['aced_questions']
            self.save_questions(part, data)

    def load_questions(self, subject_part, section):
        data = self.all_data.get(subject_part, {"sections": {}})
        sections = data.get("sections", {})
        if section not in sections:
            sections[section] = {"section_name": section, "questions": [], "aced_questions": []}
        section_data = sections[section]
        questions = section_data.get("questions", [])
        for q in questions:
            q["section_name"] = section_data.get("section_name", section)
        return questions

    def save_questions(self, subject_part, data):
        self.all_data[subject_part] = data  # Update in-memory data
        filename = f"{subject_part}.json"
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)  # Save to file for persistence
    def get_quiz_time(self):
        return pygame.time.get_ticks() - self.quiz_start_time

    def reset_timer(self):
        self.quiz_start_time = pygame.time.get_ticks()
        self.last_submit_time = 0
        play_safe(SOUND_BUTTON_CLICK)

# QuizScreen class
class QuizScreen:
    def __init__(self, state):
        self.state = state
        self.answer_box = InputBox(600, 500, 200, 40)
        self.answer_box.parent = self
        self.current_question_index = 0
        self.image_rect = pygame.Rect(30, 100, 500, 500)
        self.progress_bar = ProgressBar(100, 20, 200, 20)
        self.buttons = [
            Button(50, 610, 120, 50, "Back", self.previous_question, disabled=True, parent=self),
            Button(1000, 600, 120, 50, "Next", self.next_question, disabled=True, parent=self),
            Button(1150, 600, 120, 50, "Skip", self.skip_question, parent=self),
            Button(1000, 660, 150, 50, "Main Menu", self.show_main_menu_confirmation, parent=self),  # Updated
            Button(620, 570, 150, 50, "Submit", self.check_answer, parent=self),
            Button(SCREEN_WIDTH - 222, 60, 200, 50, "Toggle Clock", self.toggle_clock, parent=self),
            Button(SCREEN_WIDTH - 222, 120, 200, 50, "Reset Timer", self.show_reset_confirmation, parent=self)
        ]
        self.ace_button = None
        self.animation = AnswerAnimation()
        self.solution_sheet = SolutionSheet()
        self.show_clock = True
        # Added attributes for question image scrolling
        self.question_scroll_y = 0
        self.question_image_height = 0
        self.question_image = None

    def previous_question(self):
        if self.current_question_index > 0 and self.state.current_session['remaining']:
            self.current_question_index -= 1
            self.state.current_question = self.state.current_session['remaining'][self.current_question_index]
            self.state.show_answer = False
            self.solution_sheet.preview_active = False
            self.ace_button = None
            self.state.tries_left = 3
            self.answer_box.text = ""
            self.update_button_states()
    def show_main_menu_confirmation(self):
        self.state.main_menu_confirmation = True

    def confirm_main_menu(self, confirm):
        if confirm:
            self.state.current_screen = "main_menu"
            self.state.current_question = None
            self.state.current_session.clear()
            self.current_question_index = 0
            self.ace_button = None
            self.answer_box.text = ""
        self.state.main_menu_confirmation = False

    def next_question(self):
        if self.current_question_index < len(self.state.current_session['remaining']) - 1 and self.state.current_session['remaining']:
            self.current_question_index += 1
            self.state.current_question = self.state.current_session['remaining'][self.current_question_index]
            self.state.show_answer = False
            self.solution_sheet.preview_active = False
            self.ace_button = None
            self.state.tries_left = 3
            self.answer_box.text = ""
            self.update_button_states()

    def skip_question(self):
        if self.state.current_session['remaining']:
            remaining = self.state.current_session['remaining']
            if self.state.randomize:
                skipped = remaining.pop(self.current_question_index)
                remaining.append(skipped)
                self.current_question_index = (self.current_question_index + 1) % len(remaining)
            else:
                self.current_question_index = (self.current_question_index + 1) % len(remaining)
            self.state.current_question = remaining[self.current_question_index]
            self.state.show_answer = False
            self.solution_sheet.preview_active = False
            self.ace_button = None
            self.state.tries_left = 3
            self.answer_box.text = ""
            self.update_button_states()

    def check_answer(self):
        try:
            if not self.state.current_question:
                return
                
            current_time = pygame.time.get_ticks()
            if current_time - self.state.last_submit_time < SUBMIT_COOLDOWN:
                self.animation.start(False)
                self.animation.message = "Please wait before submitting again"
                play_safe(SOUND_INCORRECT)
                return
                
            user_answer = self.answer_box.text.lower().strip()
            print(f"check_answer called with user_answer: '{user_answer}'")  # Debug log
            correct_answer = self.state.current_question['answer'].lower().strip()
            
            # Normalize tags for comparison
            tags = [tag.lower().replace('-', '_') for tag in self.state.current_question.get("tags", [])]
            is_multi_choice = any(variation.replace('-', '_') in tags for variation in MULTI_CHOICE_VARIATIONS)
            is_fill_in = any(variation.replace('-', '_') in tags for variation in FILL_IN_VARIATIONS)

            if not user_answer:
                self.animation.start(False)
                self.animation.message = "Come on, at least try :("
                play_safe(SOUND_INCORRECT)
                self.answer_box.text = ""
                self.ace_button = None
                self.update_button_states()
                return

            correct = user_answer == correct_answer

            if is_multi_choice:
                if len(user_answer) == 1 and user_answer in 'abcd':
                    if correct:
                        motivational = random.choice(MOTIVATIONAL_SPEECHES)
                        self.animation.start(True)
                        self.animation.message = f"Correct :) {motivational}"
                        play_safe(SOUND_CORRECT)
                        self.state.tries_left = 3
                        question_id = self.state.current_question.get('id')
                        already_aced = question_id in self.state.current_session['aced_in_session']
                        if not already_aced:
                            self.ace_button = Button(620, 630, 150, 40, "Ace Question", self.state.ace_question, parent=self)
                        else:
                            self.ace_button = None
                        self.answer_box.text = ""
                        self.state.current_session['solved'].add(self.current_question_index)
                    else:
                        self.animation.start(False)
                        self.animation.message = "Incorrect :("
                        play_safe(SOUND_INCORRECT)
                        self.state.tries_left -= 1
                        self.answer_box.text = ""
                        self.ace_button = None
                elif len(user_answer) == 1 and user_answer not in 'abcd':
                    self.animation.start(False)
                    self.animation.message = "That letter is not in the answers :("
                    play_safe(SOUND_INCORRECT)
                    self.answer_box.text = ""
                    self.ace_button = None
                    self.update_button_states()
                    return
                elif any(char.isdigit() for char in user_answer) or '.' in user_answer or ',' in user_answer:
                    self.animation.start(False)
                    self.animation.message = "We are in multi-choice, not fill-ins!"
                    play_safe(SOUND_INCORRECT)
                    self.answer_box.text = ""
                    self.ace_button = None
                    self.update_button_states()
                    return
                else:
                    if correct:
                        motivational = random.choice(MOTIVATIONAL_SPEECHES)
                        self.animation.start(True)
                        self.animation.message = f"Correct :) {motivational}"
                        play_safe(SOUND_CORRECT)
                        self.state.tries_left = 3
                        question_id = self.state.current_question.get('id')
                        already_aced = question_id in self.state.current_session['aced_in_session']
                        if not already_aced:
                            self.ace_button = Button(620, 630, 150, 40, "Ace Question", self.state.ace_question, parent=self)
                        else:
                            self.ace_button = None
                        self.answer_box.text = ""
                        self.state.current_session['solved'].add(self.current_question_index)
                    else:
                        self.animation.start(False)
                        self.animation.message = "Incorrect :("
                        play_safe(SOUND_INCORRECT)
                        self.state.tries_left -= 1
                        self.answer_box.text = ""
                        self.ace_button = None

            elif is_fill_in:
                if len(user_answer) == 1 and user_answer in 'abcd':
                    self.animation.start(False)
                    self.animation.message = "We are in fill-ins, not multi-choice!"
                    play_safe(SOUND_INCORRECT)
                    self.answer_box.text = ""
                    self.ace_button = None
                    if self.state.tries_left == 2:
                        real_answer_sheet = self.state.current_question.get("answer_sheet", None)
                        if real_answer_sheet:
                            self.solution_sheet.start_preview("Meshes/answer_sheet.png", real_answer_sheet)
                    self.state.tries_left -= 1
                    self.update_button_states()
                    return
                elif any(char.isdigit() for char in user_answer) or '.' in user_answer or ',' in user_answer:
                    self.animation.start(False)
                    self.animation.message = "We are in fill-ins, not multi-choice!"
                    play_safe(SOUND_INCORRECT)
                    self.answer_box.text = ""
                    self.ace_button = None
                    if self.state.tries_left == 2:
                        real_answer_sheet = self.state.current_question.get("answer_sheet", None)
                        if real_answer_sheet:
                            self.solution_sheet.start_preview("Meshes/answer_sheet.png", real_answer_sheet)
                    self.state.tries_left -= 1
                    self.update_button_states()
                    return
                elif correct:
                    motivational = random.choice(MOTIVATIONAL_SPEECHES)
                    self.animation.start(True)
                    self.animation.message = f"Correct :) {motivational}"
                    play_safe(SOUND_CORRECT)
                    self.state.tries_left = 3
                    question_id = self.state.current_question.get('id')
                    already_aced = question_id in self.state.current_session['aced_in_session']
                    if not already_aced:
                        self.ace_button = Button(620, 630, 150, 40, "Ace Question", self.state.ace_question, parent=self)
                    else:
                        self.ace_button = None
                    self.answer_box.text = ""
                    self.state.current_session['solved'].add(self.current_question_index)
                else:
                    self.animation.start(False)
                    self.animation.message = "Incorrect :("
                    play_safe(SOUND_INCORRECT)
                    self.state.tries_left -= 1
                    self.answer_box.text = ""
                    self.ace_button = None
                    if self.state.tries_left == 2:
                        real_answer_sheet = self.state.current_question.get("answer_sheet", None)
                        if real_answer_sheet:
                            self.solution_sheet.start_preview("Meshes/answer_sheet.png", real_answer_sheet)

            else:
                # Default case for untagged or unrecognized questions
                print(f"Question type not recognized, processing as default. Tags: {self.state.current_question.get('tags', [])}")
                if correct:
                    motivational = random.choice(MOTIVATIONAL_SPEECHES)
                    self.animation.start(True)
                    self.animation.message = f"Correct :) {motivational}"
                    play_safe(SOUND_CORRECT)
                    self.state.tries_left = 3
                    question_id = self.state.current_question.get('id')
                    already_aced = question_id in self.state.current_session['aced_in_session']
                    if not already_aced:
                        self.ace_button = Button(620, 630, 150, 40, "Ace Question", self.state.ace_question, parent=self)
                    else:
                        self.ace_button = None
                    self.state.current_session['solved'].add(self.current_question_index)
                else:
                    self.animation.start(False)
                    self.animation.message = "Incorrect :("
                    play_safe(SOUND_INCORRECT)
                    self.state.tries_left -= 1
                    self.ace_button = None
                    if self.state.tries_left == 2:
                        real_answer_sheet = self.state.current_question.get("answer_sheet", None)
                        if real_answer_sheet:
                            self.solution_sheet.start_preview("Meshes/answer_sheet.png", real_answer_sheet)
                self.answer_box.text = ""

            self.state.last_submit_time = current_time  # Only set for valid submissions
            self.update_button_states()
        except Exception as e:
            print(f"Error in check_answer: {e}")

    def update_button_states(self):
        remaining = self.state.current_session['remaining']
        total_questions = len(remaining)
        current_time = pygame.time.get_ticks()
        for btn in self.buttons:
            if btn.text == "Back":
                btn.disabled = self.current_question_index <= 0 or not remaining
            elif btn.text == "Next":
                btn.disabled = (self.current_question_index >= total_questions - 1 or
                                self.current_question_index not in self.state.current_session['solved'])
            elif btn.text == "Skip":
                btn.disabled = not remaining
            elif btn.text == "Submit":
                btn.disabled = not self.state.current_question or (current_time - self.state.last_submit_time < SUBMIT_COOLDOWN)
        if self.ace_button:
            question_id = self.state.current_question.get('id')
            already_aced = any(q['id'] == question_id for section in self.state.aced_questions[self.state.current_part]
                               for q in self.state.aced_questions[self.state.current_part][section])
            if already_aced:
                self.ace_button = None

    def toggle_clock(self):
        self.show_clock = not self.show_clock
        play_safe(SOUND_BUTTON_CLICK)

    def show_reset_confirmation(self):
        self.state.reset_timer_confirmation = True
        play_safe(SOUND_BUTTON_CLICK)

    def confirm_reset_timer(self, confirm):
        if confirm:
            self.state.reset_timer()
        self.state.reset_timer_confirmation = False
            
    def draw(self, screen):
        if self.state.current_screen != "quiz":
            return

        screen.fill(WHITE)
        if not self.state.current_session['remaining']:
            self.state.current_screen = "main_menu"
            return

        # Draw section name with wrapping
        section_text = self.state.current_question.get("section_name", "Unknown Section")
        draw_wrapped_text(screen, f"Section: {section_text}", 30, 50, font, BLACK, 500)

        # Draw tags with wrapping
        if "tags" in self.state.current_question:
            tags_text = ", ".join(self.state.current_question["tags"])
            draw_wrapped_text(screen, f"Tags: {tags_text}", 30, 77, font, BLACK, 500)

        # Image handling
        try:
            img_path = self.state.current_question['image']
            img = pygame.image.load(img_path).convert_alpha()
            orig_width, orig_height = img.get_size()
            if orig_width <= 500:
                scaled_width = orig_width
                scaled_height = orig_height
                self.question_image = img
            else:
                scale_factor = 500 / orig_width
                scaled_width = 500
                scaled_height = int(orig_height * scale_factor)
                self.question_image = pygame.transform.scale(img, (scaled_width, scaled_height))
            self.question_image_height = scaled_height
            if scaled_height > 500:
                src_y = self.question_scroll_y
                src_height = min(500, scaled_height - src_y)
                src_rect = pygame.Rect(0, src_y, scaled_width, src_height)
                x = 30 + (500 - scaled_width) // 2
                screen.blit(self.question_image, (x, 100), src_rect)
                scroll_text = font.render("Scroll to view the full image", True, GRAY)
                screen.blit(scroll_text, (550, 150))
            else:
                x = 30 + (500 - scaled_width) // 2
                y = 100 + (500 - scaled_height) // 2
                screen.blit(self.question_image, (x, y))
                self.question_scroll_y = 0
        except Exception as e:
            print(f"Error loading image: {e}")
            img = pygame.Surface((500, 500))
            img.fill(GRAY)
            img.blit(font.render("Missing Image", True, BLACK), (10, 10))
            screen.blit(img, (30, 100))
            self.question_scroll_y = 0

        pygame.draw.rect(screen, BLACK, self.image_rect, 2)

        # Progress bar update and draw
        initial_total = self.state.current_session['total_questions']
        current_remaining = len(self.state.current_session['remaining'])
        aced_count = initial_total - current_remaining
        progress = aced_count / initial_total if initial_total > 0 else 0
        self.progress_bar.update()  # Update animation state without forcing a new value
        self.progress_bar.draw(screen)

        # Rest of the draw method
        total_questions = len(self.state.current_session['remaining'])
        current_display = self.current_question_index + 1
        progress_text = font.render(f"{current_display}/{total_questions}", True, BLACK)
        screen.blit(progress_text, (20, 20))

        self.answer_box.draw(screen)

        for btn in self.buttons:
            btn.update_hover(pygame.mouse.get_pos())
            btn.draw(screen)
        if self.ace_button:
            self.ace_button.update_hover(pygame.mouse.get_pos())
            self.ace_button.draw(screen)

        if self.state.show_answer:
            answer_text = large_font.render(self.state.current_question['answer'], True, BLACK)
            screen.blit(answer_text, (SCREEN_WIDTH // 2 - answer_text.get_width() // 2 - 100,
                                    SCREEN_HEIGHT // 2 - answer_text.get_height() // 2))

        self.animation.update()
        if pygame.time.get_ticks() - self.animation.start_time < ANIMATION_DURATION + 500:
            self.animation.draw_animation(screen)
        self.solution_sheet.draw(screen)

        if self.show_clock:
            quiz_time = self.state.get_quiz_time()
            minutes = quiz_time // 60000
            seconds = (quiz_time % 60000) // 1000
            time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
            screen.blit(time_text, (SCREEN_WIDTH - 200, 20))

        if self.state.reset_timer_confirmation:
            popup_width, popup_height = 400, 200
            popup_x, popup_y = (SCREEN_WIDTH - popup_width) // 2, (SCREEN_HEIGHT - popup_height) // 2
            pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
            text = font.render("Are you sure you want to reset the timer?", True, BLACK)
            screen.blit(text, (popup_x + (popup_width - text.get_width()) // 2, popup_y + 20))

            yes_btn = Button(popup_x + 100, popup_y + 120, 80, 40, "Yes", lambda: self.confirm_reset_timer(True))
            no_btn = Button(popup_x + 220, popup_y + 120, 80, 40, "No", lambda: self.confirm_reset_timer(False))

            yes_btn.update_hover(pygame.mouse.get_pos())
            no_btn.update_hover(pygame.mouse.get_pos())
            yes_btn.draw(screen)
            no_btn.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    yes_btn.handle_event(event)
                    no_btn.handle_event(event)

        copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
        screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

# AcedViewScreen class
class AcedViewScreen:
    def __init__(self, state):
        self.state = state
        self.current_aced_index = 0
        self.image_rect = pygame.Rect(30, 100, 500, 500)
        self.buttons = [
            Button(600, 570, 150, 50, "Unace", self.show_unace_confirmation),
            Button(1150, 570, 120, 50, "Main Menu", lambda: setattr(self.state, 'current_screen', 'main_menu')),
            Button(1150, 630, 120, 50, "Back", lambda: setattr(self.state, 'current_screen', 'aced_section_select'))
        ]
        # Add a dedicated back button for the no-aced-questions case
        self.no_aced_back_btn = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "Back",
            lambda: setattr(self.state, 'current_screen', 'aced_section_select')  # Changed to 'aced_section_select' for consistency
        )
        self.unace_confirmation = False
        self.selected_question_id = None
        self.slider = None
        self.show_image_popup = False
        self.popup_image = None
        self.popup_answer = None
        self.close_button = None
        self.current_section = None
        self.solution_sheet = SolutionSheet()

    def draw(self, screen):
        screen.fill(WHITE)
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]

        if not aced_list:
            # Use the persistent no_aced_back_btn instead of creating a new one
            self.no_aced_back_btn.update_hover(pygame.mouse.get_pos())
            self.no_aced_back_btn.draw(screen)
            text = font.render("No aced questions in this section", True, BLACK)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            return

        # Rest of the existing draw logic for when there are aced questions
        if not self.slider or self.slider.max_value != max(0, len(aced_list) - 1):
            self.slider = Slider(100, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 200, 20, 0, max(0, len(aced_list) - 1))
            self.slider.value = self.current_aced_index

        if self.current_aced_index < len(aced_list):
            question = aced_list[self.current_aced_index]

            try:
                img = pygame.image.load(question['image'])
                img = pygame.transform.scale(img, (500, 500))
            except Exception:
                img = pygame.Surface((500, 500))
                img.fill(GRAY)
                img.blit(font.render("Missing Image", True, BLACK), (10, 10))
            screen.blit(img, (30, 100))
            pygame.draw.rect(screen, BLACK, self.image_rect, 2)

            id_text = large_font.render(f"ID: {question['id']}", True, BLACK)
            screen.blit(id_text, (30, 30))

            section_text = font.render(question.get("section_name", ""), True, BLACK)
            screen.blit(section_text, (30 + (500 - section_text.get_width()) // 2, 50))

            for btn in self.buttons:
                btn.update_hover(pygame.mouse.get_pos())
                btn.draw(screen)

            if self.unace_confirmation:
                popup_width, popup_height = 400, 200
                popup_x, popup_y = (SCREEN_WIDTH - popup_width) // 2, (SCREEN_HEIGHT - popup_height) // 2
                pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
                text = font.render("Confirm unacing this question?", True, BLACK)
                screen.blit(text, (popup_x + (popup_width - text.get_width()) // 2, popup_y + 20))

                yes_btn = Button(popup_x + 100, popup_y + 120, 80, 40, "Yes", lambda: self.confirm_unace(True))
                no_btn = Button(popup_x + 220, popup_y + 120, 80, 40, "No", lambda: self.confirm_unace(False))

                yes_btn.update_hover(pygame.mouse.get_pos())
                no_btn.update_hover(pygame.mouse.get_pos())
                yes_btn.draw(screen)
                no_btn.draw(screen)

            if self.slider:
                self.slider.draw(screen)

            self.solution_sheet.draw(screen)

            if self.show_image_popup and self.popup_image and self.popup_answer:
                popup_width, popup_height = 700, 500
                popup_x, popup_y = (SCREEN_WIDTH - popup_width) // 2, (SCREEN_HEIGHT - popup_height) // 2
                pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
                screen.blit(self.popup_image, (popup_x + (popup_width - self.popup_image.get_width()) // 2, popup_y + 20))
                answer_text = large_font.render(self.popup_answer, True, BLACK)
                screen.blit(answer_text, (popup_x + (popup_width - answer_text.get_width()) // 2,
                                         popup_y + 420))
                self.close_button.update_hover(pygame.mouse.get_pos())
                self.close_button.draw(screen)

    def previous_aced(self):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        if aced_list and self.current_aced_index > 0:
            self.current_aced_index -= 1
            self.slider.value = self.current_aced_index
            self.update_button_states()

    def next_aced(self):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        if aced_list and self.current_aced_index < len(aced_list) - 1:
            self.current_aced_index += 1
            self.slider.value = self.current_aced_index
            self.update_button_states()

    def show_unace_confirmation(self):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        if aced_list:
            self.selected_question_id = aced_list[self.current_aced_index]['id']
            self.unace_confirmation = True

    def confirm_unace(self, confirm):
        if confirm and self.selected_question_id:
            self.state.unace_question(self.state.current_part, self.state.current_section, self.selected_question_id)
            aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
            if self.current_aced_index >= len(aced_list):
                self.current_aced_index = max(0, len(aced_list) - 1)
            self.slider = Slider(100, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 200, 20, 0, max(0, len(aced_list) - 1))
            self.slider.value = self.current_aced_index
            self.selected_question_id = None
            self.unace_confirmation = False
            self.update_button_states()
        else:
            self.unace_confirmation = False

    def update_button_states(self):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        for btn in self.buttons:
            if btn.text == "Unace":
                btn.disabled = not aced_list or self.current_aced_index >= len(aced_list)
            elif btn.text in ["Main Menu", "Back"]:
                btn.disabled = False

    def handle_image_click(self, pos):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        if aced_list and self.image_rect.collidepoint(pos):
            question = aced_list[self.current_aced_index]
            try:
                self.popup_image = pygame.image.load(question['image']).convert_alpha()
                self.popup_image = pygame.transform.scale(self.popup_image, (600, 400))
                self.popup_answer = question['answer']
                self.show_image_popup = True
                self.close_button = Button(SCREEN_WIDTH - 40, 50, 30, 30, "X", self.close_popup)
            except Exception as e:
                print(f"Error loading popup image: {e}")
                self.popup_image = pygame.Surface((600, 400))
                self.popup_image.fill(GRAY)
                self.popup_image.blit(font.render("Missing Image", True, BLACK), (10, 10))
                self.popup_answer = question['answer']
                self.show_image_popup = True
                self.close_button = Button(SCREEN_WIDTH - 40, 50, 30, 30, "X", self.close_popup)
            play_safe(SOUND_BUTTON_CLICK)

    def close_popup(self):
        self.show_image_popup = False
        self.popup_image = None
        self.popup_answer = None
        self.close_button = None
        play_safe(SOUND_BUTTON_CLICK)

    def handle_slider(self, mouse_pos, events):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        if aced_list and self.slider:
            self.slider.update(mouse_pos, events)
            self.current_aced_index = int(self.slider.value)
            self.current_aced_index = max(0, min(self.current_aced_index, len(aced_list) - 1))
            self.update_button_states()

    def draw(self, screen):
        screen.fill(WHITE)
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]

        if not aced_list:
            back_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "Back",
                              lambda: setattr(self.state, 'current_screen', 'main_menu'))
            back_btn.update_hover(pygame.mouse.get_pos())
            back_btn.draw(screen)
            text = font.render("No aced questions in this section", True, BLACK)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            return

        if not self.slider or self.slider.max_value != max(0, len(aced_list) - 1):
            self.slider = Slider(100, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 200, 20, 0, max(0, len(aced_list) - 1))
            self.slider.value = self.current_aced_index

        if self.current_aced_index < len(aced_list):
            question = aced_list[self.current_aced_index]

            try:
                img = pygame.image.load(question['image'])
                img = pygame.transform.scale(img, (500, 500))
            except Exception:
                img = pygame.Surface((500, 500))
                img.fill(GRAY)
                img.blit(font.render("Missing Image", True, BLACK), (10, 10))
            screen.blit(img, (30, 100))
            pygame.draw.rect(screen, BLACK, self.image_rect, 2)

            id_text = large_font.render(f"ID: {question['id']}", True, BLACK)
            screen.blit(id_text, (30, 30))

            section_text = font.render(question.get("section_name", ""), True, BLACK)
            screen.blit(section_text, (30 + (500 - section_text.get_width()) // 2, 50))

            for btn in self.buttons:
                btn.update_hover(pygame.mouse.get_pos())
                btn.draw(screen)

            if self.unace_confirmation:
                popup_width, popup_height = 400, 200
                popup_x, popup_y = (SCREEN_WIDTH - popup_width) // 2, (SCREEN_HEIGHT - popup_height) // 2
                pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
                text = font.render("Confirm unacing this question?", True, BLACK)
                screen.blit(text, (popup_x + (popup_width - text.get_width()) // 2, popup_y + 20))

                yes_btn = Button(popup_x + 100, popup_y + 120, 80, 40, "Yes", lambda: self.confirm_unace(True))
                no_btn = Button(popup_x + 220, popup_y + 120, 80, 40, "No", lambda: self.confirm_unace(False))

                yes_btn.update_hover(pygame.mouse.get_pos())
                no_btn.update_hover(pygame.mouse.get_pos())
                yes_btn.draw(screen)
                no_btn.draw(screen)

            if self.slider:
                self.slider.draw(screen)

            self.solution_sheet.draw(screen)

            if self.show_image_popup and self.popup_image and self.popup_answer:
                popup_width, popup_height = 700, 500
                popup_x, popup_y = (SCREEN_WIDTH - popup_width) // 2, (SCREEN_HEIGHT - popup_height) // 2
                pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
                screen.blit(self.popup_image, (popup_x + (popup_width - self.popup_image.get_width()) // 2, popup_y + 20))
                answer_text = large_font.render(self.popup_answer, True, BLACK)
                screen.blit(answer_text, (popup_x + (popup_width - answer_text.get_width()) // 2,
                                         popup_y + 420))
                self.close_button.update_hover(pygame.mouse.get_pos())
                self.close_button.draw(screen)

# SettingsScreen class
class SettingsScreen:
    def __init__(self, state):
        self.state = state
        self.randomize_button = Button(100, 200, 250, 50, f"Randomize: {'ON' if state.randomize else 'OFF'}", self.toggle_randomize)
        self.volume_sliders = {
            'click': {'value': VOLUMES['click'], 'x': 300, 'y': 300, 'width': 200, 'height': 20},
            'correct': {'value': VOLUMES['correct'], 'x': 300, 'y': 350, 'width': 200, 'height': 20},
            'incorrect': {'value': VOLUMES['incorrect'], 'x': 300, 'y': 400, 'width': 200, 'height': 20}
        }
        self.buttons = [
            Button(100, 100, 200, 50, "Back", lambda: setattr(self.state, 'current_screen', 'main_menu')),
            self.randomize_button
        ]
        self.load_settings()

    def load_settings(self):
        try:
            with open(os.path.join(DATA_DIR, 'settings.json'), 'r') as f:
                settings = json.load(f)
                for key in settings:
                    if key == 'randomize':
                        self.state.randomize = settings[key]
                    elif key in VOLUMES:
                        VOLUMES[key] = settings[key]
                        self.volume_sliders[key]['value'] = settings[key]
            SOUND_BUTTON_CLICK.set_volume(VOLUMES['click'])
            SOUND_CORRECT.set_volume(VOLUMES['correct'])
            SOUND_INCORRECT.set_volume(VOLUMES['incorrect'])
            SOUND_PAPER_FOLD.set_volume(VOLUMES['click'])
        except FileNotFoundError:
            print("No settings file found. Using default volumes and settings.")
        except json.JSONDecodeError:
            print("Invalid settings.json. Using default volumes and settings.")

    def save_settings(self):
        settings = {'randomize': self.state.randomize}
        for key in VOLUMES:
            settings[key] = VOLUMES[key]
        with open(os.path.join(DATA_DIR, 'settings.json'), 'w') as f:
            json.dump(settings, f, indent=2)
        SOUND_BUTTON_CLICK.set_volume(VOLUMES['click'])
        SOUND_CORRECT.set_volume(VOLUMES['correct'])
        SOUND_INCORRECT.set_volume(VOLUMES['incorrect'])
        SOUND_PAPER_FOLD.set_volume(VOLUMES['click'])

    def toggle_randomize(self):
        self.state.randomize = not self.state.randomize
        self.randomize_button.text = f"Randomize: {'ON' if self.state.randomize else 'OFF'}"
        self.save_settings()

    def handle_events(self, events):
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for key, slider in self.volume_sliders.items():
                    slider_rect = pygame.Rect(slider['x'], slider['y'], slider['width'], slider['height'])
                    if slider_rect.collidepoint(mouse_pos):
                        relative_x = mouse_pos[0] - slider['x']
                        slider['value'] = max(0.0, min(1.0, relative_x / slider['width']))
                        VOLUMES[key] = slider['value']
                        self.save_settings()

    def draw(self, screen):
        screen.fill(WHITE)
        for btn in self.buttons:
            btn.update_hover(pygame.mouse.get_pos())
            btn.draw(screen)
        for key, slider in self.volume_sliders.items():
            pygame.draw.rect(screen, GRAY, (slider['x'], slider['y'], slider['width'], slider['height']))
            knob_x = slider['x'] + int(slider['value'] * slider['width'])
            pygame.draw.circle(screen, BUTTON_COLOR, (knob_x, slider['y'] + slider['height'] // 2), 10)
            label = font.render(f"{key.capitalize()} Volume: {slider['value']:.2f}", True, BLACK)
            screen.blit(label, (slider['x'], slider['y'] - 30))
        copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
        screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

# Screen handler functions
def handle_main_menu(state, events, mouse_pos):
    button_width = 250  # Minimum width
    button_height = 50
    spacing = 20
    start_y = 200  # Adjusted to give space for title
    y = start_y
    buttons = []
    
    # Button definitions
    button_configs = [
        ("Start", lambda: setattr(state, 'current_screen', 'part_select'), FOLDER_ICON),
        ("Settings", lambda: setattr(state, 'current_screen', 'settings'), DRIVE_ICON),
        ("Aced Questions", lambda: setattr(state, 'current_screen', 'aced_select'), TROPHY_ICON)
    ]
    
    for text, callback, icon in button_configs:
        btn = Button(0, y, button_width, button_height, text, callback, icon=icon)
        btn.x = SCREEN_WIDTH // 2 - btn.width // 2
        btn.rect.x = btn.x
        buttons.append(btn)
        y += btn.height + spacing
    
    # Draw elements
    title = font.render("SAT Study Helper", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
        btn.draw(screen)
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

def handle_settings_screen(state, events, mouse_pos):
    state.settings.handle_events(events)
    state.settings.draw(screen)
    
def handle_part_selection(state, events, mouse_pos):
    screen.fill(WHITE)
    button_width = 200  # Minimum width
    button_height = 50
    spacing = 20
    num_columns = 3
    total_buttons = len(SUBJECT_PARTS)
    buttons_per_column = (total_buttons + num_columns - 1) // num_columns  # Ceiling division
    total_columns = (total_buttons + buttons_per_column - 1) // buttons_per_column  # Actual number of columns needed
    total_width = total_columns * button_width + (total_columns - 1) * spacing
    left_margin = (SCREEN_WIDTH - total_width) // 2  # Center the entire grid
    start_y = 100

    buttons = []
    current_index = 0
    for col in range(total_columns):
        x = left_margin + col * (button_width + spacing)
        num_buttons = min(buttons_per_column, total_buttons - current_index)
        column_parts = SUBJECT_PARTS[current_index:current_index + num_buttons]
        current_index += num_buttons
        for i, part in enumerate(column_parts):
            y = start_y + i * (button_height + spacing)
            btn = Button(
                x, y, button_width, button_height,
                part.replace('1', ' 1').replace('2', ' 2').replace('3', ' 3').replace('4', ' 4').capitalize(),
                lambda p=part: setattr(state, 'current_part', p) or setattr(state, 'current_screen', 'section_select'),
                icon=FOLDER_ICON
            )
            buttons.append(btn)

    # Add back button at the bottom, centered
    back_btn = Button(
        SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT - button_height - 20,
        button_width, button_height, "Back",
        lambda: setattr(state, 'current_screen', 'main_menu'),
        icon=DRIVE_ICON
    )
    buttons.append(back_btn)

    title = font.render("Select Subject Part", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
        btn.draw(screen)
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

def handle_aced_section_select(state, events, mouse_pos):
    screen.fill(WHITE)
    button_width = 320  # Increased from 300
    button_height = 50
    spacing = 20
    sections = state.all_data[state.current_part].get("sections", {})
    start_y = 100
    y = start_y
    buttons = []
    
    for section_key, section_data in sections.items():
        section_name = section_data.get("section_name", section_key.capitalize())
        aced_count = len(state.aced_questions[state.current_part].get(section_key, []))
        btn_text = f"{section_name} ({aced_count} aced)"
        btn = Button(
            0, y, button_width, button_height,
            btn_text,
            lambda sk=section_key: setattr(state, 'current_section', sk) or setattr(state, 'current_screen', 'aced_view'),
            icon=FOLDER_ICON
        )
        btn.x = SCREEN_WIDTH // 2 - btn.width // 2
        btn.rect.x = btn.x
        buttons.append(btn)
        y += btn.height + spacing
    
    back_btn = Button(
        0, y, button_width, button_height,
        "Back",
        lambda: setattr(state, 'current_screen', 'aced_select'),
        icon=DRIVE_ICON
    )
    back_btn.x = SCREEN_WIDTH // 2 - back_btn.width // 2
    back_btn.rect.x = back_btn.x
    buttons.append(back_btn)
    
    title = font.render(f"Aced Questions in {state.current_part.replace('1', ' 1').replace('2', ' 2').replace('3', ' 3').replace('4', ' 4').capitalize()}", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
        btn.draw(screen)
    
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

def handle_aced_select(state, events, mouse_pos):
    screen.fill(WHITE)
    button_width = 200  # Minimum width
    button_height = 50
    spacing = 20
    num_columns = 3
    total_buttons = len(SUBJECT_PARTS)  # Define total_buttons
    buttons_per_column = (total_buttons + num_columns - 1) // num_columns  # Ceiling division
    total_columns = (total_buttons + buttons_per_column - 1) // buttons_per_column  # Actual number of columns needed
    total_width = total_columns * button_width + (total_columns - 1) * spacing
    left_margin = (SCREEN_WIDTH - total_width) // 2  # Center the entire grid
    start_y = 100

    buttons = []
    current_index = 0
    for col in range(total_columns):
        x = left_margin + col * (button_width + spacing)
        num_buttons = min(buttons_per_column, total_buttons - current_index)
        column_parts = SUBJECT_PARTS[current_index:current_index + num_buttons]
        current_index += num_buttons
        for i, part in enumerate(column_parts):
            y = start_y + i * (button_height + spacing)
            btn = Button(
                x, y, button_width, button_height,
                part.replace('1', ' 1').replace('2', ' 2').replace('3', ' 3').replace('4', ' 4').capitalize(),
                lambda p=part: setattr(state, 'current_part', p) or setattr(state, 'current_screen', 'aced_section_select'),
                icon=FOLDER_ICON
            )
            buttons.append(btn)

    # Add back button at the bottom, centered
    back_btn = Button(
        SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT - button_height - 20,
        button_width, button_height, "Back",
        lambda: setattr(state, 'current_screen', 'main_menu'),
        icon=DRIVE_ICON
    )
    buttons.append(back_btn)

    title = font.render("Select Subject Part for Aced Questions", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
        btn.draw(screen)
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

def handle_quiz_screen(state, events, mouse_pos):
    if state.current_screen != "quiz":
        return
    
    # Update button states every frame
    state.quiz.update_button_states()
    
    # Define popup variables upfront
    popup_width, popup_height = 400, 200
    popup_x = (SCREEN_WIDTH - popup_width) // 2
    popup_y = (SCREEN_HEIGHT - popup_height) // 2
    yes_btn = None
    no_btn = None
    
    # Handle events based on confirmation state
    if state.main_menu_confirmation or state.reset_timer_confirmation:
        if state.main_menu_confirmation:
            yes_btn = Button(popup_x + popup_width // 4 - 40, popup_y + 120, 80, 40, "Yes", lambda: state.quiz.confirm_main_menu(True))
            no_btn = Button(popup_x + 3 * popup_width // 4 - 40, popup_y + 120, 80, 40, "No", lambda: state.quiz.confirm_main_menu(False))
        elif state.reset_timer_confirmation:
            yes_btn = Button(popup_x + popup_width // 4 - 40, popup_y + 120, 80, 40, "Yes", lambda: state.quiz.confirm_reset_timer(True))
            no_btn = Button(popup_x + 3 * popup_width // 4 - 40, popup_y + 120, 80, 40, "No", lambda: state.quiz.confirm_reset_timer(False))
        
        for event in events:
            if yes_btn:
                yes_btn.handle_event(event)
            if no_btn:
                no_btn.handle_event(event)
    else:
        # Handle regular quiz screen events
        for btn in state.quiz.buttons:
            btn.update_hover(mouse_pos)
            for event in events:
                btn.handle_event(event)
        if state.quiz.ace_button:
            state.quiz.ace_button.update_hover(mouse_pos)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if state.quiz.ace_button.rect.collidepoint(event.pos):
                        state.quiz.ace_button.callback()  # Execute the callback explicitly
                        print(f"Ace button clicked for question {state.quiz.state.current_question['id']}")  # Debug
                        state.quiz.ace_button = None  # Clear after execution
        for event in events:
            state.quiz.answer_box.handle_event(event)
            state.quiz.solution_sheet.handle_event(event, state.quiz)
    
    # Draw the quiz screen
    state.quiz.draw(screen)
    
    # Draw confirmation popups
    if state.main_menu_confirmation:
        pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
        wrapped_lines = textwrap.wrap("Return to Main Menu?", width=(popup_width - 40) // font.size(" ")[0])
        max_line_width = max([font.size(line)[0] for line in wrapped_lines], default=0)
        text_x = popup_x + (popup_width - max_line_width) // 2
        text_y = popup_y + 20
        for line in wrapped_lines:
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (text_x, text_y))
            text_y += font.get_height()
        if yes_btn and no_btn:
            yes_btn.update_hover(mouse_pos)
            no_btn.update_hover(mouse_pos)
            yes_btn.draw(screen)
            no_btn.draw(screen)
    elif state.reset_timer_confirmation:
        pygame.draw.rect(screen, GRAY, (popup_x, popup_y, popup_width, popup_height))
        wrapped_lines = textwrap.wrap("Are you sure you want to reset the timer?", width=(popup_width - 40) // font.size(" ")[0])
        max_line_width = max([font.size(line)[0] for line in wrapped_lines], default=0)
        text_x = popup_x + (popup_width - max_line_width) // 2
        text_y = popup_y + 20
        for line in wrapped_lines:
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (text_x, text_y))
            text_y += font.get_height()
        if yes_btn and no_btn:
            yes_btn.update_hover(mouse_pos)
            no_btn.update_hover(mouse_pos)
            yes_btn.draw(screen)
            no_btn.draw(screen)
        
def handle_section_selection(state, events, mouse_pos):
    screen.fill(WHITE)
    button_width = 320  # Increased from 300
    button_height = 50
    spacing = 20
    sections = state.all_data[state.current_part].get("sections", {})
    start_y = 100
    y = start_y
    buttons = []
    
    for section_key, section_data in sections.items():
        section_name = section_data.get("section_name", section_key.capitalize())
        btn = Button(
            0, y, button_width, button_height,
            section_name,
            lambda sk=section_key: state.start_new_session(state.current_part, [sk]),
            icon=FOLDER_ICON
        )
        btn.x = SCREEN_WIDTH // 2 - btn.width // 2
        btn.rect.x = btn.x
        buttons.append(btn)
        y += btn.height + spacing
    
    all_btn = Button(
        0, y, button_width, button_height,
        "All Sections",
        lambda: state.start_new_session(state.current_part, list(sections.keys())),
        icon=FOLDER_ICON
    )
    all_btn.x = SCREEN_WIDTH // 2 - all_btn.width // 2
    all_btn.rect.x = all_btn.x
    buttons.append(all_btn)
    y += all_btn.height + spacing
    
    back_btn = Button(
        0, y, button_width, button_height,
        "Back",
        lambda: setattr(state, 'current_screen', 'part_select'),
        icon=DRIVE_ICON
    )
    back_btn.x = SCREEN_WIDTH // 2 - back_btn.width // 2
    back_btn.rect.x = back_btn.x
    buttons.append(back_btn)
    
    title = font.render(f"Select Sections for {state.current_part.replace('1', ' 1').replace('2', ' 2').replace('3', ' 3').replace('4', ' 4').capitalize()}", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
        btn.draw(screen)
    
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

# Main game loop
def main():
    """Main game loop with functional item-by-item JSON preloading."""
    initialize_json_files()
    
    state = GameState()
    state.quiz = QuizScreen(state)
    state.settings = SettingsScreen(state)
    state.aced_view = AcedViewScreen(state)

    # Preload all JSON files with a loading screen
    total_files = len(SUBJECT_PARTS)
    loaded_files = 0
    for part in SUBJECT_PARTS:
        filename = f"{part}.json"
        filepath = os.path.join(DATA_DIR, filename)
        data = load_json(filepath)
        message = f"Loaded from {filepath}"
        draw_loading_screen(screen, message)
        state.all_data[part] = data
        loaded_files += 1
        # Optional: Add a progress indicator (e.g., "X/Y files loaded")
        progress_message = f"{loaded_files}/{total_files} files loaded"
        progress_text = font.render(progress_message, True, WHITE)
        progress_rect = progress_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(progress_text, progress_rect)
        pygame.display.flip()
    
    # Load aced questions after all data is preloaded
    state.load_aced_questions()

    while True:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state.current_screen == "quiz" and event.type == pygame.MOUSEWHEEL:
                if pygame.Rect(30, 100, 500, 500).collidepoint(mouse_pos) and state.quiz.question_image_height > 500:
                    state.quiz.question_scroll_y = max(0, min(state.quiz.question_scroll_y - event.y * 30, state.quiz.question_image_height - 500))
                    print(f"Mouse wheel event: Adjusted scroll_y to {state.quiz.question_scroll_y}")

        screen.fill(WHITE)
        if state.current_screen == "main_menu":
            handle_main_menu(state, events, mouse_pos)
        elif state.current_screen == "part_select":
            handle_part_selection(state, events, mouse_pos)
        elif state.current_screen == "section_select":
            handle_section_selection(state, events, mouse_pos)
        elif state.current_screen == "quiz":
            handle_quiz_screen(state, events, mouse_pos)
        elif state.current_screen == "aced_select":
            handle_aced_select(state, events, mouse_pos)
        elif state.current_screen == "aced_section_select":
            handle_aced_section_select(state, events, mouse_pos)
        elif state.current_screen == "aced_view":
            state.aced_view.draw(screen)
            if state.aced_view.unace_confirmation:
                popup_width, popup_height = 400, 200
                popup_x, popup_y = (SCREEN_WIDTH - popup_width) // 2, (SCREEN_HEIGHT - popup_height) // 2
                yes_btn = Button(popup_x + 100, popup_y + 120, 80, 40, "Yes", lambda: state.aced_view.confirm_unace(True))
                no_btn = Button(popup_x + 220, popup_y + 120, 80, 40, "No", lambda: state.aced_view.confirm_unace(False))
                for event in events:
                    yes_btn.handle_event(event)
                    no_btn.handle_event(event)
            else:
                aced_list = state.aced_view.state.aced_questions[state.aced_view.state.current_part][state.aced_view.state.current_section]
                for event in events:
                    state.aced_view.handle_slider(mouse_pos, [event])
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        state.aced_view.handle_image_click(event.pos)
                    for btn in state.aced_view.buttons:
                        btn.handle_event(event)
                    if not aced_list:
                        state.aced_view.no_aced_back_btn.handle_event(event)
        elif state.current_screen == "settings":
            handle_settings_screen(state, events, mouse_pos)

        pygame.display.flip()
        clock.tick(30)
if __name__ == "__main__":
    main()