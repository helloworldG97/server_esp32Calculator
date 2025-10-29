import socket
import json
import subprocess
import sys
import re
import math
import os

# Server configuration - Use environment variable for port (required for cloud platforms)
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = int(os.environ.get('PORT', 5000))  # Railway/Render will provide PORT

def is_math_related(text):
    """Check if the input contains math-related content"""
    math_keywords = ['solve', 'calculate', 'math', 'equation', 'formula', 'function',
                    'derivative', 'integral', 'algebra', 'geometry', 'trigonometry',
                    'calculus', 'statistics', 'probability', 'matrix', 'vector',
                    'graph', 'plot', 'prime', 'factor', 'polynomial', 'theorem',
                    'proof', 'angle', 'area', 'volume', 'percentage', 'ratio']

    math_symbols = ['+', '-', '*', '/', '=', '^', '√', 'π', '∞', '∑', '∫', '∂', '∆']

    text_lower = text.lower()
    if any(keyword in text_lower for keyword in math_keywords):
        return True

    if any(symbol in text for symbol in math_symbols):
        return True

    math_patterns = [
        r'\d+\s*[\+\-\*\/]\s*\d+',
        r'[xX]\s*[\+\-\*\/]\s*[yY]',
        r'[fF]\(x\)',
        r'\d+\s*=\s*\d+',
        r'[0-9]+\^[0-9]+',
    ]

    for pattern in math_patterns:
        if re.search(pattern, text):
            return True

    return False

def solve_math_problem(problem):
    """Attempt to solve math problems programmatically"""
    try:
        problem = problem.lower().strip()

        if re.match(r'^\d+[\+\-\*\/]\d+$', problem.replace(' ', '')):
            return f"Solution: {eval(problem)}"

        if 'prime' in problem and 'number' in problem:
            numbers = re.findall(r'\d+', problem)
            if numbers:
                num = int(numbers[0])
                if num > 1:
                    for i in range(2, int(math.sqrt(num)) + 1):
                        if num % i == 0:
                            return f"{num} is not a prime number (divisible by {i})"
                    return f"{num} is a prime number"

        if 'area' in problem:
            if 'circle' in problem:
                numbers = re.findall(r'\d+', problem)
                if numbers:
                    r = int(numbers[0])
                    area = math.pi * r * r
                    return f"Area of circle with radius {r} = π × {r}² = {area:.2f}"

            if 'rectangle' in problem or 'square' in problem:
                numbers = re.findall(r'\d+', problem)
                if len(numbers) >= 2:
                    l, w = int(numbers[0]), int(numbers[1])
                    return f"Area = length × width = {l} × {w} = {l * w}"

        return None

    except Exception as e:
        return f"Math solving error: {str(e)}"

def generate_llm_response(prompt):
    """Generate response using local LLM or fallback to simple responses"""
    try:
        # Try to use Ollama if available
        result = subprocess.run(
            ['ollama', 'run', 'kimi-k2:1t-cloud', prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        if result.returncode == 0 and result.stdout:
            advice = result.stdout.strip()
            advice = re.sub(r'\n+', '\n', advice)
            return advice
        else:
            error_msg = result.stderr if result.stderr else "No response from LLM"
            return f"Error from LLM: {error_msg}"

    except FileNotFoundError:
        # Ollama not available - provide simple response
        return "Cloud server response: I'm running in cloud mode without LLM. For complex queries, please ensure Ollama is installed on the server."
    except subprocess.TimeoutExpired:
        return "Error: LLM request timed out (60 seconds)."
    except Exception as e:
        return f"Error calling LLM: {str(e)}"

def analyze_user_message(user_message):
    """Analyze user message and generate appropriate response"""

    if is_math_related(user_message):
        print("[Info] Math-related question detected")
        math_solution = solve_math_problem(user_message)
        if math_solution and not math_solution.startswith("Math solving error"):
            return math_solution

        math_prompt = (
            f"Please solve this math problem with clear step-by-step explanation:\n"
            f"Problem: {user_message}\n\n"
            f"Provide the solution in this format:\n"
            f"1. First, explain what the problem is asking\n"
            f"2. Show each step clearly with explanations\n"
            f"3. Provide the final answer with proper units if applicable\n"
            f"4. Keep it educational and easy to understand"
        )
        return generate_llm_response(math_prompt)

    bp_pattern = r'(\d+)\s*\/\s*(\d+).*?(\d+)\s*(?:bpm|heart|hr)'
    bp_match = re.search(bp_pattern, user_message.lower())

    if bp_match:
        print("[Info] Blood pressure data detected in message")
        systolic = int(bp_match.group(1))
        diastolic = int(bp_match.group(2))
        heart_rate = int(bp_match.group(3))

        bp_prompt = (
            f"Act as a cheerful, concise medical advisor. "
            f"Given BP: {systolic}/{diastolic} mmHg, Heart Rate: {heart_rate} bpm. "
            f"Provide brief health advice (3-5 sentences). "
            f"Be positive and practical with specific lifestyle tips."
        )
        return generate_llm_response(bp_prompt)

    print("[Info] General question detected")
    general_prompt = (
        f"Please answer this question in a helpful, conversational way:\n"
        f"Question: {user_message}\n\n"
        f"Keep your response clear, concise, and friendly. "
        f"If it's a complex topic, break it down into simple steps."
    )
    return generate_llm_response(general_prompt)

def start_server():
    """Start TCP server to receive data from ESP32"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print("=" * 60)
    print("Universal AI Assistant Server - CLOUD VERSION")
    print("=" * 60)
    print(f"Server listening on {HOST}:{PORT}")
    print("Waiting for ESP32 connections...")
    print("\nThis server can handle:")
    print("• Math problems (solve, calculate, equations)")
    print("• General questions (science, history, etc.)")
    print("• Blood pressure analysis (BP 120/80 HR 75)")
    print("• Any other text-based queries")
    print("=" * 60 + "\n")

    def recv_line(conn):
        """Receive until newline or connection close."""
        buf = b""
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                break
            buf += chunk
            if b"\n" in buf:
                break
        return buf.decode('utf-8', errors='replace').strip()

    def format_response(text: str) -> str:
        """Format the response for better readability"""
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()

    while True:
        try:
            client, address = server.accept()
            print(f"\n[Connected] ESP32 connected from {address}")

            data = recv_line(client)
            print(f"[Received] {data}")

            try:
                json_data = json.loads(data)

                if 'user_message' in json_data:
                    user_message = json_data['user_message']
                    print(f"[Message] User input: {user_message}")
                    print("[Processing] Analyzing message type and generating response...")

                    response = analyze_user_message(user_message)

                elif 'systolic' in json_data and 'diastolic' in json_data:
                    systolic = json_data['systolic']
                    diastolic = json_data['diastolic']
                    heart_rate = json_data.get('heart_rate', 75)

                    print(f"[Vitals] BP: {systolic}/{diastolic} mmHg | HR: {heart_rate} bpm")
                    print("[Processing] Generating health advice...")

                    bp_prompt = (
                        f"Act as a cheerful medical advisor. "
                        f"Given BP: {systolic}/{diastolic} mmHg, Heart Rate: {heart_rate} bpm. "
                        f"Provide brief health advice (3-5 sentences). "
                        f"Be positive and practical."
                    )
                    response = generate_llm_response(bp_prompt)

                else:
                    response = "Error: Unknown message format. Expected 'user_message' or BP data."

                response = format_response(response)

                print("\n" + "=" * 60)
                print("AI RESPONSE:")
                print("=" * 60)
                print(response)
                print("=" * 60 + "\n")

                client.send((response + "\n").encode('utf-8'))
                print("[Sent] Response sent back to ESP32\n")

            except json.JSONDecodeError as e:
                error_msg = f"Error: Invalid JSON format - {str(e)}"
                print(f"[Error] {error_msg}")
                client.send((error_msg + "\n").encode('utf-8'))
            except KeyError as e:
                error_msg = f"Error: Missing field in data: {e}"
                print(f"[Error] {error_msg}")
                client.send((error_msg + "\n").encode('utf-8'))
            except Exception as e:
                error_msg = f"Error processing request: {str(e)}"
                print(f"[Error] {error_msg}")
                client.send((error_msg + "\n").encode('utf-8'))

            client.close()
            print("[Disconnected] ESP32 disconnected")

        except KeyboardInterrupt:
            print("\n\nServer shutting down...")
            break
        except Exception as e:
            print(f"[Error] {str(e)}")
            try:
                client.close()
            except:
                pass

    server.close()
    print("Server closed. Goodbye!")

if __name__ == "__main__":
    start_server()