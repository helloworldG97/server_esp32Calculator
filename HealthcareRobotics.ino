#include <WiFi.h>

// WiFi credentials
const char* ssid = "Nepthys";
const char* password = "darylace";

// Cloud server configuration
// IMPORTANT: Replace this with your actual cloud server domain/IP after deployment
const char* serverHost = "your-app-name.railway.app";  // Example: "daryl-codex.railway.app"
const int serverPort = 443;  // Use 443 for HTTPS, or the port your service provides
const bool useHTTPS = true;  // Set to true if using HTTPS

// For direct IP (if using AWS EC2 or similar)
// const char* serverHost = "54.123.45.67";  // Your cloud server IP
// const int serverPort = 5000;
// const bool useHTTPS = false;

// Variables to store user input
String userMessage = "";
bool newDataAvailable = false;

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("ESP32 IP address: ");
  Serial.println(WiFi.localIP());

  // Instructions for user
  Serial.println("\n╔════════════════════════════════════════════════════════╗");
  Serial.println("║                         DARYL                          ║");
  Serial.println("║                   CODEX_AI - CLOUD                     ║");
  Serial.println("╠════════════════════════════════════════════════════════╣");
  Serial.println("║    im DARYL_CODEX_AI a fully functional cheating       ║");
  Serial.println("║                      CALCULATOR                        ║");
  Serial.println("║                    (Cloud Version)                     ║");
  Serial.println("║                                                        ║");
  Serial.println("║ Examples:                                              ║");
  Serial.println("║   - Integral                                           ║");
  Serial.println("║   - Physics                                            ║");
  Serial.println("║   - Basic questions                                    ║");
  Serial.println("╚════════════════════════════════════════════════════════╝\n");
  Serial.print("Connected to cloud server: ");
  Serial.println(serverHost);
  Serial.println("\nReady for input. Type your message and press ENTER:");
}

void sendUserMessage(String message) {
  WiFiClient client;

  Serial.println("\nConnecting to cloud server...");

  if (client.connect(serverHost, serverPort)) {
    Serial.println("Connected to cloud server!");

    // Create JSON payload
    String data = "{\"user_message\":\"" + message + "\"}";

    // Send the data
    client.println(data);
    Serial.println("Sent: " + data);

    Serial.println("DarylCodex_ai is parsing...");
    
    // Wait for response with timeout
    unsigned long timeout = millis();
    while (client.available() == 0) {
      if (millis() - timeout > 30000) {  // 30 second timeout for cloud
        Serial.println("Timeout waiting for response!");
        client.stop();
        return;
      }
      delay(100);
    }

    // Read ALL response data
    String fullResponse = "";
    Serial.println("\n╔════════════════════════════════════════════════════════╗");
    Serial.println("║           RESPONSE FROM CLOUD SERVER                   ║");
    Serial.println("╚════════════════════════════════════════════════════════╝\n");

    while (client.available()) {
      char c = client.read();
      Serial.print(c);  // Print each character as it arrives
      fullResponse += c;
      delay(1);  // Small delay to ensure we get all data
    }
    
    Serial.println("\n\n╔════════════════════════════════════════════════════════╗");
    Serial.println("║                 END OF RESPONSE                        ║");
    Serial.println("╚════════════════════════════════════════════════════════╝\n");

    client.stop();
  } else {
    Serial.println("Connection to cloud server failed!");
    Serial.println("Please check:");
    Serial.println("1. Server hostname is correct");
    Serial.println("2. Server is running");
    Serial.println("3. Port is correct");
    Serial.println("4. WiFi connection is stable");
  }
}

void checkSerialInput() {
  static String inputBuffer = "";

  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') { 
      if (inputBuffer.length() > 0) {
        userMessage = inputBuffer;
        newDataAvailable = true;
        inputBuffer = "";  
      }
    } else if (c != '\r') { 
      inputBuffer += c;
    }

    delay(2);  // Small delay for stable reading
  }
}

void loop() {
  // Check for new input from Serial Monitor
  checkSerialInput();

  // If new data is available, send it to the cloud server
  if (newDataAvailable) {
    Serial.print("Sending message: ");
    Serial.println(userMessage);

    sendUserMessage(userMessage);
    newDataAvailable = false;

    Serial.println("\nReady for next input...");
    Serial.println("Type your message and press ENTER:");
  }

  delay(1000);  
}