import pygame
import sys
import json
import os
import random
import textwrap
import math

# Initialize Pygame and mixer early
pygame.mixer.init()
pygame.init()

# Set application icon
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
COPYRIGHT_TEXT = "© Educa College Prep - All Rights of 'sat_data' Reserved, more info on readme"
DATA_DIR = "sat_data"

# Load icons with fallback (including trophy icon) - Larger size (36x36)
if not os.path.exists('Meshes/folder_icon.png'):
    print("Warning: Missing folder_icon.png")
    FOLDER_ICON = pygame.Surface((36, 36))
    FOLDER_ICON.fill(GRAY)
else:
    FOLDER_ICON = pygame.image.load('Meshes/folder_icon.png')
    FOLDER_ICON = pygame.transform.scale(FOLDER_ICON, (36, 36))  # Larger size for button fit

if not os.path.exists('Meshes/drive.png'):
    print("Warning: Missing drive.png")
    DRIVE_ICON = pygame.Surface((36, 36))
    DRIVE_ICON.fill(GRAY)
else:
    DRIVE_ICON = pygame.image.load('Meshes/drive.png')
    DRIVE_ICON = pygame.transform.scale(DRIVE_ICON, (36, 36))  # Larger size for button fit

if not os.path.exists('Meshes/trophy.png'):
    print("Warning: Missing trophy.png")
    TROPHY_ICON = pygame.Surface((36, 36))
    TROPHY_ICON.fill(GRAY)
else:
    TROPHY_ICON = pygame.image.load('Meshes/trophy.png')
    TROPHY_ICON = pygame.transform.scale(TROPHY_ICON, (36, 36))  # Larger size for button fit

# Volume and animation settings
VOLUMES = {'click': 1.0, 'correct': 1.0, 'incorrect': 1.0}
ANIMATION_DURATION = 2000  # 2 seconds in milliseconds
SUBMIT_COOLDOWN = 1000  # 1 second cooldown in milliseconds

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

# Initialize JSON files if missing or invalid
def initialize_json_files():
    for part in ['geometry1', 'geometry2']:
        filepath = os.path.join(DATA_DIR, f"{part}.json")
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            default_data = {
                "sections": {
                    "sectionA": {"section_name": "Section A", "questions": [], "aced_questions": []},
                    "sectionB": {"section_name": "Section B", "questions": [], "aced_questions": []}
                }
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)
                print(f"Initialized {filepath} with default data")

# Utility functions
def draw_wrapped_text(surface, text, x, y, font, color, max_width):
    wrapped_lines = textwrap.wrap(text, width=max_width // font.size(" ")[0])
    y_offset = 0
    for line in wrapped_lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + y_offset))
        y_offset += font.get_height()

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content or content in ['{}', '[]']:
                print(f"{filepath} is empty or minimal, returning default")
                return {"sections": {}}
            data = json.loads(content)
            print(f"Loaded {filepath}: {data}")
            return data
    except json.JSONDecodeError as e:
        print(f"Error loading {filepath}: Invalid JSON format - {str(e)}")
        return {"sections": {}}
    except FileNotFoundError:
        print(f"Warning: {filepath} not found. Returning default structure.")
        return {"sections": {}}

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

# SolutionSheet class
class SolutionSheet:
    def __init__(self):
        self.preview_active = False
        self.opened = False
        self.sheet_image = None
        self.real_answer_sheet = None
        self.preview_width = 290
        self.preview_height = 290
        self.full_width = 500
        self.full_height = 500
        self.preview_x = SCREEN_WIDTH - self.preview_width - 90
        self.preview_y = 200
        self.x = self.preview_x
        self.y = self.preview_y
        self.width = self.preview_width
        self.height = self.preview_height
        self.hovered = False
        self.close_rect = None
        self.close_hovered = False

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
                    self.sheet_image = pygame.image.load(self.real_answer_sheet).convert_alpha()
                    self.sheet_image = pygame.transform.scale(self.sheet_image, (self.full_width, self.full_height))
                    self.width = self.full_width
                    self.height = self.full_height
                    self.x = SCREEN_WIDTH - self.full_width - 225  # Moved more to the left (from -100 to -250)
                    self.y = (SCREEN_HEIGHT - self.height) // 2
                    self.opened = True
                except Exception as e:
                    print(f"Error loading real answer sheet: {e}")
                    self.sheet_image = pygame.Surface((self.full_width, self.full_height), pygame.SRCALPHA)
                    self.sheet_image.fill((0, 0, 0, 0))
                    self.width = self.full_width
                    self.height = self.full_height
                    self.x = SCREEN_WIDTH - self.full_width - 250  # Consistent positioning
                    self.y = (SCREEN_HEIGHT - self.height) // 2
                    self.opened = True
            else:
                # Reset to preview state
                try:
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
            play_safe(SOUND_PAPER_FOLD)

    def handle_event(self, event, quiz_screen):
        if event.type == pygame.MOUSEBUTTONDOWN and self.preview_active:
            mouse_pos = event.pos
            current_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if self.opened and self.close_rect and self.close_rect.collidepoint(mouse_pos):
                self.toggle_open()
            elif not self.opened and current_rect.collidepoint(mouse_pos):
                self.toggle_open()
                if quiz_screen.state.current_question and "answer_sheet" in quiz_screen.state.current_question:
                    self.real_answer_sheet = quiz_screen.state.current_question['answer_sheet']

    def draw(self, screen):
        if not self.preview_active:
            return
        self.update()
        current_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        if self.opened:
            screen.blit(self.sheet_image, current_rect)
            # Draw close button (white X on red background), positioned to not overlap
            self.close_rect = pygame.Rect(
                current_rect.right - 40,  # Inside top-right corner of the sheet
                current_rect.top - 40,    # Above the sheet
                30, 30                    # Size of close button
            )
            close_color = (200, 0, 0) if self.close_hovered else (255, 0, 0)  # Red background
            pygame.draw.rect(screen, close_color, self.close_rect)
            # Draw white X using lines
            pygame.draw.line(screen, WHITE, 
                           (self.close_rect.x + 5, self.close_rect.y + 5), 
                           (self.close_rect.x + 25, self.close_rect.y + 25), 2)
            pygame.draw.line(screen, WHITE, 
                           (self.close_rect.x + 25, self.close_rect.y + 5), 
                           (self.close_rect.x + 5, self.close_rect.y + 25), 2)
        else:
            color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
            pygame.draw.rect(screen, color, current_rect)
            screen.blit(self.sheet_image, current_rect)
            answer_sheet_text = large_font.render("Answer Sheet", True, BLACK)
            screen.blit(answer_sheet_text, (current_rect.x, current_rect.bottom + 10))
# Button class with icon support
class Button:
    def __init__(self, x, y, width, height, text, callback, disabled=False, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.disabled = disabled
        self.icon = icon  # Optional icon (e.g., folder_icon, drive.png, or trophy.png)

    def draw(self, surface):
        color = GRAY if self.disabled else (BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR)
        pygame.draw.rect(surface, color, self.rect)
        if self.icon:
            # Draw icon on the left with padding
            icon_x = self.rect.x + 10  # 10 pixels padding from left
            icon_y = self.rect.centery - self.icon.get_height() // 2
            surface.blit(self.icon, (icon_x, icon_y))
            # Draw text to the right of the icon
            text_surf = font.render(self.text, True, TEXT_COLOR)
            text_x = icon_x + self.icon.get_width() + 10  # 10 pixels padding after icon
            text_y = self.rect.centery - text_surf.get_height() // 2
            surface.blit(text_surf, (text_x, text_y))
        else:
            text_surf = font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def update_hover(self, mouse_pos):
        self.hovered = not self.disabled and self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if not self.disabled and event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            play_safe(SOUND_BUTTON_CLICK)
            self.callback()

# InputBox class
class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.parent = None  # Add parent reference

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.parent:
                    self.parent.check_answer()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surf = font.render(self.text, True, BLACK)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

# Slider class for aced questions navigation
class Slider:
    def __init__(self, x, y, width, height, min_value, max_value):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value if max_value > min_value else min_value + 1  # Ensure max_value > min_value
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
                if self.rect.width > 0:  # Ensure width is not zero to avoid division by zero
                    self.value = self.min_value + (self.max_value - self.min_value) * (relative_x / self.rect.width)
                    self.value = max(self.min_value, min(self.max_value, round(self.value)))

    def draw(self, screen):
        if self.max_value == self.min_value:
            # If max_value equals min_value, draw a static handle at the start
            handle_x = self.rect.x
            handle_rect = pygame.Rect(handle_x, self.rect.y - (self.handle_height - self.rect.height) / 2, self.handle_width, self.handle_height)
            pygame.draw.rect(screen, BUTTON_COLOR, handle_rect)
        else:
            pygame.draw.rect(screen, GRAY, self.rect)
            if self.rect.width > 0:  # Ensure width is not zero to avoid division by zero
                handle_x = self.rect.x + (self.value - self.min_value) * (self.rect.width - self.handle_width) / (self.max_value - self.min_value)
                handle_rect = pygame.Rect(handle_x, self.rect.y - (self.handle_height - self.rect.height) / 2, self.handle_width, self.handle_height)
                pygame.draw.rect(screen, BUTTON_COLOR, handle_rect)

# GameState class
class GameState:
    def __init__(self):
        self.current_screen = "main_menu"
        self.current_part = None
        self.current_sections = []
        self.current_session = {'remaining': [], 'total_questions': 0, 'aced_in_session': set(), 'solved': set()}
        self.current_question = None
        self.tries_left = 3
        self.show_answer = False
        self.randomize = False
        self.last_submit_time = 0
        self.quiz_start_time = 0
        self.reset_timer_confirmation = False
        self.current_question_index = 0
        # Store aced questions by part and section
        self.aced_questions = {
            'geometry1': {'sectionA': [], 'sectionB': []},
            'geometry2': {'sectionA': [], 'sectionB': []}
        }
        self.load_aced_questions()
        self.show_image_popup = False  # New state for image popup in AcedView

    def can_submit(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_submit_time >= SUBMIT_COOLDOWN

    def get_quiz_time(self):
        if self.current_screen == "quiz" and self.quiz_start_time > 0:
            return pygame.time.get_ticks() - self.quiz_start_time
        return 0

    def reset_timer(self):
        self.quiz_start_time = pygame.time.get_ticks()
        self.reset_timer_confirmation = False

    def start_new_session(self, subject_part, sections):
        print(f"Starting session for {subject_part} with sections: {sections}")
        self.current_part = subject_part
        self.current_sections = sections
        all_questions = []
        for section in sections:
            questions = load_questions(subject_part, section)
            all_questions.extend(questions)
        
        if not all_questions:
            print("No questions found, returning to main menu")
            self.current_screen = "main_menu"
            return
        
        # Include only unaced questions in the session
        self.current_session['remaining'] = [q for q in all_questions 
                                          if q.get('id') not in {aq['id'] for s in self.aced_questions[subject_part].values() 
                                                               for aq in s}]
        self.current_session['aced_in_session'] = set()
        self.current_session['solved'] = set()
        
        if not self.current_session['remaining']:
            print("All questions aced, showing completion message")
            self.show_completion_message()
            return
        
        if self.randomize:
            random.shuffle(self.current_session['remaining'])
        
        self.current_session['total_questions'] = len(self.current_session['remaining'])
        self.current_screen = "quiz"
        self.current_question_index = 0
        self.current_question = self.current_session['remaining'][self.current_question_index]
        self.quiz_start_time = pygame.time.get_ticks()
        self.last_submit_time = 0
        self.reset_timer_confirmation = False
        self.tries_left = 3
        print(f"Session started with {len(self.current_session['remaining'])} questions")

    def ace_question(self):
        if self.current_question and self.current_part and self.current_sections:
            print(f"Attempting to ace question: {self.current_question}")
            if 'id' not in self.current_question:
                print("Error: Current question has no 'id' field")
                return
            
            question_id = self.current_question['id']
            # Find which section this question belongs to
            for section in self.current_sections:
                questions = load_questions(self.current_part, section)
                if any(q['id'] == question_id for q in questions):
                    self.save_aced_question(self.current_part, section, self.current_question.copy())
                    self.current_session['aced_in_session'].add(question_id)
                    break
            
            # Remove the aced question from remaining and skip to next unaced question
            if self.current_question and self.current_question['id'] in [q['id'] for q in self.current_session['remaining']]:
                self.current_session['remaining'] = [q for q in self.current_session['remaining'] 
                                                  if q['id'] != question_id]
                if not self.current_session['remaining']:
                    self.show_completion_message()
                    return
                
                # Adjust current_question_index and move to next unaced question
                if self.current_question_index >= len(self.current_session['remaining']):
                    self.current_question_index = 0
                self.current_question = self.current_session['remaining'][self.current_question_index]
            
            # Check if all questions in current sections are aced
            all_aced = True
            for section in self.current_sections:
                section_questions = load_questions(self.current_part, section)
                if not all(q['id'] in {aq['id'] for aq in self.aced_questions[self.current_part][section]} 
                          for q in section_questions):
                    all_aced = False
                    break
            
            if all_aced:
                self.show_completion_message()
                return
        else:
            print("No current question or part/sections to ace")

    def show_completion_message(self):
        screen.fill(WHITE)
        text = large_font.render("All questions aced in this section, congrats!", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)  # 3 seconds delay
        self.current_screen = "main_menu"  # Ensure return to main menu
        self.current_question = None
        self.current_session.clear()

    def load_aced_questions(self):
        for part in ['geometry1', 'geometry2']:
            data = load_json(os.path.join(DATA_DIR, f"{part}.json"))
            sections = data.get("sections", {})
            for section in sections:
                self.aced_questions[part][section] = sections[section].get('aced_questions', [])

    def save_aced_question(self, part, section, question):
        if 'id' not in question:
            print("Error: Question lacks 'id' field")
            return
            
        # Load current data
        data = load_json(os.path.join(DATA_DIR, f"{part}.json"))
        sections = data.get("sections", {})
        
        if section not in sections:
            sections[section] = {"section_name": section, "questions": [], "aced_questions": []}
        
        # Ensure aced_questions exists in the section
        if 'aced_questions' not in sections[section]:
            sections[section]['aced_questions'] = []
        
        # Add to aced questions if not already there
        if not any(q['id'] == question['id'] for q in sections[section]['aced_questions']):
            sections[section]['aced_questions'].append(question)
            self.aced_questions[part][section].append(question)
            
        # Save updated data
        save_questions(part, data)

    def unace_question(self, part, section, question_id):
        data = load_json(os.path.join(DATA_DIR, f"{part}.json"))
        sections = data.get("sections", {})
        
        if section in sections and 'aced_questions' in sections[section]:
            sections[section]['aced_questions'] = [q for q in sections[section]['aced_questions'] 
                                               if q['id'] != question_id]
            self.aced_questions[part][section] = sections[section]['aced_questions']
            save_questions(part, data)

# QuizScreen class
class QuizScreen:
    def __init__(self, state):
        self.state = state
        self.answer_box = InputBox(600, 500, 200, 40)
        self.answer_box.parent = self
        self.current_question_index = 0
        self.image_rect = pygame.Rect(30, 100, 500, 500)
        self.buttons = [
            Button(50, 610, 120, 50, "Back", self.previous_question),
            Button(1000, 600, 120, 50, "Next", self.next_question, disabled=True),
            Button(1150, 600, 120, 50, "Skip", self.skip_question),
            Button(1000, 660, 150, 50, "Main Menu", lambda: setattr(self.state, 'current_screen', 'main_menu')),
            Button(620, 570, 150, 50, "Submit", self.check_answer),
            Button(SCREEN_WIDTH - 222, 60, 200, 50, "Toggle Clock", self.toggle_clock),
            Button(SCREEN_WIDTH - 222, 120, 200, 50, "Reset Timer", self.show_reset_confirmation)
        ]
        self.ace_button = None
        self.animation = AnswerAnimation()
        self.solution_sheet = SolutionSheet()
        self.show_clock = True

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
        if self.state.current_session['remaining'] and self.current_question_index not in self.state.current_session['solved']:
            skipped = self.state.current_session['remaining'].pop(self.current_question_index)
            self.state.current_session['remaining'].append(skipped)
            if self.current_question_index >= len(self.state.current_session['remaining']):
                self.current_question_index = 0
            self.state.current_question = self.state.current_session['remaining'][self.current_question_index]
            self.state.show_answer = False
            self.solution_sheet.preview_active = False
            self.ace_button = None
            self.state.tries_left = 3
            self.answer_box.text = ""
            self.update_button_states()

    def check_answer(self):
        if not self.state.can_submit():
            return
        try:
            if not self.state.current_question:
                return
            user_answer = self.answer_box.text.lower()
            correct_answer = self.state.current_question['answer'].lower()
            correct = user_answer == correct_answer
            self.animation.start(correct)
            if correct:
                play_safe(SOUND_CORRECT)
                self.state.tries_left = 3
                self.ace_button = Button(620, 630, 150, 40, "Ace Question", self.state.ace_question)
                self.answer_box.text = ""
                self.state.current_session['solved'].add(self.current_question_index)
            else:
                play_safe(SOUND_INCORRECT)
                self.state.tries_left -= 1
                self.answer_box.text = ""
                self.ace_button = None
                if self.state.tries_left == 2:  # Show after first incorrect answer (tries_left drops from 3 to 2)
                    real_answer_sheet = self.state.current_question.get("answer_sheet", None)
                    if real_answer_sheet:
                        self.solution_sheet.start_preview("Meshes/answer_sheet.png", real_answer_sheet)
            self.state.last_submit_time = pygame.time.get_ticks()
            self.update_button_states()
        except Exception as e:
            print(f"Error in check_answer: {e}")

    def update_button_states(self):
        for btn in self.buttons:
            if btn.text == "Next":
                btn.disabled = self.current_question_index not in self.state.current_session['solved']
                break

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

    def handle_image_click(self, pos):
        if self.image_rect.collidepoint(pos) and self.state.current_question:
            real_answer_sheet = self.state.current_question.get("answer_sheet", None)
            if real_answer_sheet:
                self.solution_sheet.start_preview("Meshes/answer_sheet.png", real_answer_sheet)
            play_safe(SOUND_BUTTON_CLICK)

    def draw(self, screen):
        screen.fill(WHITE)
        if not self.state.current_session['remaining']:
            self.state.current_screen = "main_menu"
            return

        if self.state.current_question:
            if "tags" in self.state.current_question:
                tags_text = ", ".join(self.state.current_question["tags"])
                tags_surf = font.render(f"Tags: {tags_text}", True, BLACK)
                screen.blit(tags_surf, (30 + (500 - tags_surf.get_width()) // 2, 70))

            section_text = font.render(self.state.current_question.get("section_name", ""), True, BLACK)
            screen.blit(section_text, (30 + (500 - section_text.get_width()) // 2, 50))

            try:
                img = pygame.image.load(self.state.current_question['image'])
                img = pygame.transform.scale(img, (500, 500))
            except Exception:
                img = pygame.Surface((500, 500))
                img.fill(GRAY)
                img.blit(font.render("Missing Image", True, BLACK), (10, 10))
            screen.blit(img, (30, 100))
            pygame.draw.rect(screen, BLACK, self.image_rect, 2)

            big_text = font.render("IMAGES OWNED BY EDUCA", True, BLACK)
            screen.blit(big_text, (90 + (500 - big_text.get_width()) // 2, 610))

            self.answer_box.draw(screen)

            for btn in self.buttons:
                btn.update_hover(pygame.mouse.get_pos())
                btn.draw(screen)
            if self.ace_button:
                self.ace_button.update_hover(pygame.mouse.get_pos())
                self.ace_button.draw(screen)

            # Update progress text to show only unaced questions
            unaced_questions = [q for q in self.state.current_session['remaining'] 
                              if q['id'] not in self.state.current_session['aced_in_session']]
            total_unaced = len(unaced_questions)
            current_unaced = self.current_question_index + 1 if self.current_question_index < total_unaced else total_unaced
            progress_text = font.render(f"{current_unaced}/{total_unaced}", True, BLACK)
            screen.blit(progress_text, (20, 20))

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
                
                for event in pygame.event.get():  # Use pygame.event.get() instead of undefined 'events'
                    yes_btn.handle_event(event)
                    no_btn.handle_event(event)

        copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
        screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

class AcedViewScreen:
    def __init__(self, state):
        self.state = state
        self.current_aced_index = 0
        self.image_rect = pygame.Rect(30, 100, 500, 500)
        self.buttons = [
            Button(600, 570, 150, 50, "Unace", self.show_unace_confirmation),
            Button(1150, 570, 120, 50, "Main Menu", lambda: setattr(self.state, 'current_screen', 'main_menu'))
        ]
        self.unace_confirmation = False
        self.selected_question_id = None
        self.slider = None  # Initialize slider dynamically based on aced questions
        self.show_image_popup = False  # Track image popup state
        self.popup_image = None  # Store the popup image
        self.popup_answer = None  # Store the popup answer
        self.close_button = None  # Button to close the popup
        self.solution_sheet = SolutionSheet()  # Keep SolutionSheet instance, but it won’t be used here

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
            self.unace_confirmation = False  # Reset if "No" is clicked

    def update_button_states(self):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        for btn in self.buttons:
            if btn.text == "Unace":
                btn.disabled = not aced_list or self.current_aced_index >= len(aced_list)
            elif btn.text == "Main Menu":
                btn.disabled = False  # Ensure Main Menu is always clickable

    def handle_image_click(self, pos):
        aced_list = self.state.aced_questions[self.state.current_part][self.state.current_section]
        if aced_list and self.image_rect.collidepoint(pos):
            question = aced_list[self.current_aced_index]
            try:
                self.popup_image = pygame.image.load(question['image']).convert_alpha()
                self.popup_image = pygame.transform.scale(self.popup_image, (600, 400))  # Scale for popup
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
            # Display "Back" button when there are no aced questions
            back_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "Back", 
                            lambda: setattr(self.state, 'current_screen', 'main_menu'))
            back_btn.update_hover(pygame.mouse.get_pos())
            back_btn.draw(screen)
            text = font.render("No aced questions in this section", True, BLACK)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            return  # Exit early, events handled in main loop

        # Initialize or update slider based on the number of aced questions
        if not self.slider or self.slider.max_value != max(0, len(aced_list) - 1):
            self.slider = Slider(100, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 200, 20, 0, max(0, len(aced_list) - 1))
            self.slider.value = self.current_aced_index

        if self.current_aced_index < len(aced_list):
            question = aced_list[self.current_aced_index]
            
            # Draw question image
            try:
                img = pygame.image.load(question['image'])
                img = pygame.transform.scale(img, (500, 500))
            except Exception:
                img = pygame.Surface((500, 500))
                img.fill(GRAY)
                img.blit(font.render("Missing Image", True, BLACK), (10, 10))
            screen.blit(img, (30, 100))
            pygame.draw.rect(screen, BLACK, self.image_rect, 2)

            # Draw question ID at top
            id_text = large_font.render(f"ID: {question['id']}", True, BLACK)
            screen.blit(id_text, (30, 30))

            # Draw section name
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
                no_btn = Button(popup_x + 220, popup_y + 120, 80, 40, "No", lambda: self.confirm_unace(False), disabled=False)
                
                yes_btn.update_hover(pygame.mouse.get_pos())
                no_btn.update_hover(pygame.mouse.get_pos())
                yes_btn.draw(screen)
                no_btn.draw(screen)
                
                for event in pygame.event.get():  # Use pygame.event.get() instead of undefined 'events'
                    yes_btn.handle_event(event)
                    no_btn.handle_event(event)

            # Draw slider at the bottom
            if self.slider:
                self.slider.draw(screen)

            # Draw solution sheet (will only appear if activated elsewhere, not here)
            self.solution_sheet.draw(screen)

            # Draw image popup if active
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
        self.randomize_button = Button(100, 200,250, 50, f"Randomize: {'ON' if state.randomize else 'OFF'}", self.toggle_randomize)
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
                    if key in VOLUMES:
                        VOLUMES[key] = settings[key]
                        self.volume_sliders[key]['value'] = settings[key]
            SOUND_BUTTON_CLICK.set_volume(VOLUMES['click'])
            SOUND_CORRECT.set_volume(VOLUMES['correct'])
            SOUND_INCORRECT.set_volume(VOLUMES['incorrect'])
            SOUND_PAPER_FOLD.set_volume(1)
        except FileNotFoundError:
            print("No settings file found. Using default volumes.")
        except json.JSONDecodeError:
            print("Invalid settings.json. Using default volumes.")

    def save_settings(self):
        with open(os.path.join(DATA_DIR, 'settings.json'), 'w') as f:
            json.dump(VOLUMES, f, indent=2)
        SOUND_BUTTON_CLICK.set_volume(VOLUMES['click'])
        SOUND_CORRECT.set_volume(VOLUMES['correct'])
        SOUND_INCORRECT.set_volume(VOLUMES['incorrect'])
        SOUND_PAPER_FOLD.set_volume(VOLUMES['click'])

    def toggle_randomize(self):
        self.state.randomize = not self.state.randomize
        self.randomize_button.text = f"Randomize: {'ON' if self.state.randomize else 'OFF'}"

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
    button_width = 200
    button_height = 50
    spacing = 20
    total_buttons = 3 
    total_height = total_buttons * button_height + (total_buttons - 1) * spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2

    buttons = [
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y, 250, button_height, 
               "Start", lambda: setattr(state, 'current_screen', 'part_select'), icon=FOLDER_ICON),
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + spacing, 250, button_height, 
               "Settings", lambda: setattr(state, 'current_screen', 'settings'), icon=DRIVE_ICON),
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + spacing), 250, button_height, 
               "Aced Questions", lambda: setattr(state, 'current_screen', 'aced_select'), icon=TROPHY_ICON)
    ]
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
    title = font.render("SAT Study Helper", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.draw(screen)
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

def handle_part_selection(state, events, mouse_pos):
    screen.fill(WHITE)
    buttons = [
        Button(SCREEN_WIDTH // 2 - 100, 200, 200, 50, "Geometry 1", 
               lambda: setattr(state, 'current_part', 'geometry1') or setattr(state, 'current_screen', 'section_select'), icon=FOLDER_ICON),
        Button(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "Geometry 2", 
               lambda: setattr(state, 'current_part', 'geometry2') or setattr(state, 'current_screen', 'section_select'), icon=FOLDER_ICON)
    ]
    title = font.render("Select Subject Part", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
        btn.draw(screen)
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

def handle_section_selection(state, events, mouse_pos):
    screen.fill(WHITE)
    button_width = 200
    button_height = 50
    spacing = 20
    total_buttons = 3
    total_height = total_buttons * button_height + (total_buttons - 1) * spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2

    buttons = [
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height, "Section A", 
               lambda: state.start_new_session(state.current_part, ["sectionA"]), icon=FOLDER_ICON),
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height, "Section B", 
               lambda: state.start_new_session(state.current_part, ["sectionB"]), icon=FOLDER_ICON),
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + spacing), button_width, button_height, "Both", 
               lambda: state.start_new_session(state.current_part, ["sectionA", "sectionB"]), icon=FOLDER_ICON)
    ]
    title = font.render(f"Select Sections for {state.current_part}", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    for btn in buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
        btn.draw(screen)
    copyright_surf = font.render(COPYRIGHT_TEXT, True, BLACK)
    screen.blit(copyright_surf, (20, SCREEN_HEIGHT - 40))

def handle_quiz_screen(state, events, mouse_pos):
    for btn in state.quiz.buttons:
        btn.update_hover(mouse_pos)
        for event in events:
            btn.handle_event(event)
    for event in events:
        state.quiz.answer_box.handle_event(event)
        state.quiz.solution_sheet.handle_event(event, state.quiz)
        if event.type == pygame.MOUSEBUTTONDOWN:
            state.quiz.handle_image_click(event.pos)
            if state.quiz.ace_button:
                state.quiz.ace_button.handle_event(event)
    state.quiz.draw(screen)

def handle_aced_select(state, events, mouse_pos):
    screen.fill(WHITE)
    buttons = [
        Button(SCREEN_WIDTH // 2 - 100, 200, 200, 50, "Geometry 1", 
               lambda: setattr(state, 'current_part', 'geometry1') or setattr(state, 'current_screen', 'aced_section_select')),
        Button(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "Geometry 2", 
               lambda: setattr(state, 'current_part', 'geometry2') or setattr(state, 'current_screen', 'aced_section_select'))
    ]
    title = font.render("Select Subject Part for Aced Questions", True, BLACK)
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
    button_width = 200
    button_height = 50
    spacing = 20
    total_buttons = 2 
    total_height = total_buttons * button_height + (total_buttons - 1) * spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2

    buttons = [
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height, "Section A", 
               lambda: setattr(state, 'current_section', 'sectionA') or setattr(state, 'current_screen', 'aced_view')),
        Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + spacing, button_width, button_height, "Section B", 
               lambda: setattr(state, 'current_section', 'sectionB') or setattr(state, 'current_screen', 'aced_view'))
    ]
    title = font.render(f"Select Section for Aced Questions in {state.current_part}", True, BLACK)
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

# Utility functions for questions
def load_questions(subject_part, section):
    filename = f"{subject_part}.json"
    filepath = os.path.join(DATA_DIR, filename)
    data = load_json(filepath)
    sections = data.get("sections", {})
    if section not in sections:
        sections[section] = {"section_name": section, "questions": [], "aced_questions": []}
        save_questions(subject_part, data)
    section_data = sections[section]
    questions = section_data.get("questions", [])
    for q in questions:
        q["section_name"] = section_data.get("section_name", section)
    return questions

def save_questions(subject_part, data):
    filename = f"{subject_part}.json"
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Main game loop
def main():
    state = GameState()
    state.quiz = QuizScreen(state)
    state.settings = SettingsScreen(state)
    state.aced_view = AcedViewScreen(state)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()  # Define events here
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill(WHITE)
        
        if state.current_screen == "main_menu":
            handle_main_menu(state, events, mouse_pos)
        elif state.current_screen == "part_select":
            handle_part_selection(state, events, mouse_pos)
        elif state.current_screen == "section_select":
            handle_section_selection(state, events, mouse_pos)
        elif state.current_screen == "quiz":
            handle_quiz_screen(state, events, mouse_pos)
        elif state.current_screen == "settings":
            handle_settings_screen(state, events, mouse_pos)
        elif state.current_screen == "aced_select":
            handle_aced_select(state, events, mouse_pos)
        elif state.current_screen == "aced_section_select":
            handle_aced_section_select(state, events, mouse_pos)
        elif state.current_screen == "aced_view":
            for btn in state.aced_view.buttons:
                btn.update_hover(mouse_pos)
                for event in events:
                    btn.handle_event(event)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    state.aced_view.handle_image_click(event.pos)
                    if state.aced_view.close_button and state.aced_view.close_button.rect.collidepoint(event.pos):
                        state.aced_view.close_button.handle_event(event)
                    if state.aced_view.solution_sheet.preview_active:
                        state.aced_view.solution_sheet.handle_event(event, state.aced_view)
            if not state.aced_view.state.aced_questions[state.aced_view.state.current_part][state.aced_view.state.current_section]:
                back_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "Back", 
                                lambda: setattr(state.aced_view.state, 'current_screen', 'main_menu'))
                back_btn.update_hover(mouse_pos)
                back_btn.handle_event(event)
                back_btn.draw(screen)
            state.aced_view.handle_slider(mouse_pos, events)
            state.aced_view.draw(screen)
        
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    initialize_json_files()
    main()