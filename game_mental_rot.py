import pygame
import os
import random
import csv
import sys

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()

# Screen parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mental Rotation Task")

# Set center coordinates
center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2

# Define a font for text messages
font = pygame.font.SysFont('Arial', 20)

# Path to your images folder
IMAGE_DIR = "stimuli"  # ensure your images are in a folder named "stimuli"

# List of image names to load.
image_names = [
    "instructions", "instruction2", "correct", "incorrect", "training", "readyforreal", "thatwasit"
]

# Add trial images: target1...target15, correct1...correct15, wrong1...wrong15.
for i in range(1, 16):
    image_names.append(f"target{i}")
for i in range(1, 16):
    image_names.append(f"correct{i}")
for i in range(1, 16):
    image_names.append(f"wrong{i}")

# Dictionary to store loaded images
images = {}

def load_images():
    for name in image_names:
        # Adjust the file extension if needed (.png assumed)
        path = os.path.join(IMAGE_DIR, f"{name}.png")
        if not os.path.exists(path):
            print(f"Warning: Image file {path} not found.")
            continue
        images[name] = pygame.image.load(path).convert_alpha()

load_images()

def draw_image(image, pos):
    """Draws an image with its center at pos."""
    rect = image.get_rect(center=pos)
    screen.blit(image, rect)
    return rect

def wait_for_key():
    """Wait until a key is pressed."""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(30)

def show_message(text_lines):
    """Display a list of text lines in the center of the screen."""
    screen.fill((255, 255, 255))
    y_offset = center_y - (len(text_lines)*20)//2
    for line in text_lines:
        txt = font.render(line, True, (0, 0, 0))
        txt_rect = txt.get_rect(center=(center_x, y_offset))
        screen.blit(txt, txt_rect)
        y_offset += 30
    pygame.display.flip()
    wait_for_key()

def run_trial(block_name, trial_num, target_name, correct_name, wrong_name):
    """
    Runs one trial.
    - Shows target image at (center_x, center_y-150)
    - Randomly places the correct image either left or right at y=center_y+150.
    - The wrong image is shown on the opposite side.
    - Displays instruction2 image at (center_x+300, center_y-200)
    - Waits for a mouse click, measures reaction time, and determines if click was on correct image.
    - Shows feedback image (correct/incorrect) at (center_x, center_y+200) for 2000ms.
    Returns reaction time (ms) and a Boolean indicating correctness.
    """
    # Randomly choose side: 0 means correct image on left, 1 means correct image on right
    side = random.randint(0, 1)
    target_pos = (center_x, center_y - 150)
    if side == 0:
        correct_pos = (center_x - 250, center_y + 150)
        wrong_pos = (center_x + 250, center_y + 150)
    else:
        correct_pos = (center_x + 250, center_y + 150)
        wrong_pos = (center_x - 250, center_y + 150)
    instruction2_pos = (center_x + 300, center_y - 200)
    feedback_pos = (center_x, center_y + 200)

    screen.fill((255, 255, 255))
    target_rect = draw_image(images[target_name], target_pos)
    correct_rect = draw_image(images[correct_name], correct_pos)
    wrong_rect = draw_image(images[wrong_name], wrong_pos)
    if "instruction2" in images:
        draw_image(images["instruction2"], instruction2_pos)
    pygame.display.flip()

    start_time = pygame.time.get_ticks()
    response = None
    rt = None

    trial_active = True
    while trial_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                rt = pygame.time.get_ticks() - start_time
                click_pos = event.pos
                if correct_rect.collidepoint(click_pos):
                    response = "correct"
                else:
                    response = "incorrect"
                trial_active = False
                break
        clock.tick(60)

    screen.fill((255, 255, 255))
    if response == "correct" and "correct" in images:
        draw_image(images["correct"], feedback_pos)
    elif response != "correct" and "incorrect" in images:
        draw_image(images["incorrect"], feedback_pos)
    pygame.display.flip()
    pygame.time.delay(2000)
    return rt, response

def run_block(block_name, trial_list):
    """
    Runs a block of trials.
    trial_list is a list of tuples: (target_name, correct_name, wrong_name).
    Returns a list of trial results (each as a dict).
    """
    results = []
    for i, (targ, corr, wrong) in enumerate(trial_list, start=1):
        rt, resp = run_trial(block_name, i, targ, corr, wrong)
        results.append({
            "Block": block_name,
            "Trial": i,
            "RT_ms": rt,
            "Response": resp
        })
    return results

def get_new_filename(prefix="results", extension="csv"):
    """Generate a new filename by incrementing a counter until an unused filename is found."""
    num = 1
    while os.path.exists(f"{prefix}{num}.{extension}"):
        num += 1
    return f"{prefix}{num}.{extension}"

def main():
    all_results = []

    # Display instructions
    if "instructions" in images:
        screen.fill((255, 255, 255))
        draw_image(images["instructions"], (center_x, center_y))
        pygame.display.flip()
        wait_for_key()
    else:
        show_message(["Instructions:", "Press any key to start training."])

    if "training" in images:
        screen.fill((255, 255, 255))
        draw_image(images["training"], (center_x, center_y))
        pygame.display.flip()
        wait_for_key()
    else:
        show_message(["Training Block", "Press any key to continue."])

    # Set up trial lists
    training_trials = []
    test_trials = []
    for i in range(1, 16):
        targ = f"target{i}"
        corr = f"correct{i}"
        wrong = f"wrong{i}"
        if i <= 5:
            training_trials.append((targ, corr, wrong))
        else:
            test_trials.append((targ, corr, wrong))

    # Run training block (5 trials)
    training_results = run_block("training", training_trials)
    all_results.extend(training_results)

    if "readyforreal" in images:
        screen.fill((255, 255, 255))
        draw_image(images["readyforreal"], (center_x, center_y))
        pygame.display.flip()
        wait_for_key()
    else:
        show_message(["Test Block", "Press any key to continue."])

    # Run test block (10 trials)
    test_results = run_block("test", test_trials)
    all_results.extend(test_results)

    # Calculate feedback
    correct_rts = [trial["RT_ms"] for trial in test_results if trial["Response"] == "correct"]
    perc_correct = (sum(1 for trial in test_results if trial["Response"] == "correct") / len(test_results)) * 100
    avg_rt = sum(correct_rts)/len(correct_rts) if correct_rts else 0

    screen.fill((255, 255, 255))
    feedback_lines = [
        f"Percentage correct (Test block): {perc_correct:.1f}%",
        f"Average RT (correct only): {avg_rt:.0f} ms",
        "Press space to continue."
    ]
    y_offset = center_y - 40
    for line in feedback_lines:
        txt = font.render(line, True, (0, 0, 0))
        txt_rect = txt.get_rect(center=(center_x, y_offset))
        screen.blit(txt, txt_rect)
        y_offset += 30
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
        clock.tick(30)

    # Automatically generate a new filename for this participant's results
    csv_file = get_new_filename(prefix="results", extension="csv")
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Block", "Trial", "RT_ms", "Response"])
        writer.writeheader()
        for trial in all_results:
            writer.writerow(trial)
    print(f"Results saved to {csv_file}")

    if "thatwasit" in images:
        screen.fill((255, 255, 255))
        draw_image(images["thatwasit"], (center_x, center_y))
        pygame.display.flip()
        pygame.time.delay(3000)
    else:
        show_message(["That was it!", "Press any key to exit."])

    pygame.quit()

if __name__ == "__main__":
    main()