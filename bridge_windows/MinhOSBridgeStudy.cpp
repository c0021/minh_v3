// MinhOSBridgeStudy.cpp - Simple Bridge Integration Study
// Optimized for MinhOS v3 Windows Bridge architecture
// Minimal, focused implementation for reliable market data export

#include "sierrachart.h"
#include <string>
#include <sstream>
#include <ctime>
#include <fstream>
#include <cmath>

SCDLLName("MinhOSBridgeStudy")

//==============================================
// BRIDGE-SPECIFIC CONFIGURATION
//==============================================

// Match exact paths expected by bridge.py
const char* MARKET_DATA_FILE = "C:/SierraChart/Data/minhos_market_data.json";
const char* TRADE_COMMANDS_FILE = "C:/SierraChart/Data/minhos_trade_commands.json";
const char* TRADE_RESPONSES_FILE = "C:/SierraChart/Data/minhos_trade_responses.json";

// Update interval (1 second to match bridge expectations)
const int UPDATE_INTERVAL_MS = 1000;
const int TRADE_CHECK_INTERVAL_MS = 500; // Check for trades more frequently

// Data validation
const double MIN_VALID_PRICE = 0.01;
const double MAX_PRICE_CHANGE_PERCENT = 50.0; // Allow larger moves for crypto/volatile assets

// Trading limits
const int MAX_POSITION_SIZE = 10;
const double MIN_STOP_DISTANCE = 1.0;

//==============================================
// JSON UTILITIES
//==============================================

std::string escapeJsonString(const std::string& input) {
    std::string result;
    result.reserve(input.length() + 10);
    
    for (char c : input) {
        switch (c) {
            case '"':  result += "\\\""; break;
            case '\\': result += "\\\\"; break;
            case '\b': result += "\\b"; break;
            case '\f': result += "\\f"; break;
            case '\n': result += "\\n"; break;
            case '\r': result += "\\r"; break;
            case '\t': result += "\\t"; break;
            default:   result += c; break;
        }
    }
    return result;
}

std::string getCurrentTimestamp() {
    time_t now = time(nullptr);
    struct tm* utc_tm = gmtime(&now);
    char timeStr[32];
    strftime(timeStr, sizeof(timeStr), "%Y-%m-%dT%H:%M:%S.000Z", utc_tm);
    return std::string(timeStr);
}

// Create JSON matching bridge.py MarketData model exactly
std::string createBridgeMarketDataJSON(SCStudyInterfaceRef& sc) {
    std::stringstream json;
    json.precision(8); // High precision for prices
    json << std::fixed;
    
    json << "{";
    json << "\"timestamp\":\"" << getCurrentTimestamp() << "\",";
    json << "\"symbol\":\"" << escapeJsonString(sc.Symbol.GetChars()) << "\",";
    json << "\"price\":" << sc.Close[sc.Index] << ",";
    json << "\"volume\":" << (int)sc.Volume[sc.Index] << ",";
    
    // Include bid/ask if available (required by bridge)
    if (sc.Bid > 0 && sc.Ask > 0) {
        json << "\"bid\":" << sc.Bid << ",";
        json << "\"ask\":" << sc.Ask;
    } else {
        // Use close price as fallback if bid/ask unavailable
        json << "\"bid\":" << sc.Close[sc.Index] << ",";
        json << "\"ask\":" << sc.Close[sc.Index];
    }
    json << "}";
    
    return json.str();
}

//==============================================
// DATA VALIDATION
//==============================================

bool isValidData(SCStudyInterfaceRef& sc) {
    double price = sc.Close[sc.Index];
    double volume = sc.Volume[sc.Index];
    
    // Basic validation
    if (price <= 0 || price < MIN_VALID_PRICE) return false;
    if (volume < 0) return false;
    if (sc.High[sc.Index] < sc.Low[sc.Index]) return false;
    if (price < sc.Low[sc.Index] || price > sc.High[sc.Index]) return false;
    
    // Check for reasonable price movement
    if (sc.Index > 0) {
        double prevPrice = sc.Close[sc.Index - 1];
        if (prevPrice > 0) {
            double changePercent = std::abs((price - prevPrice) / prevPrice * 100.0);
            if (changePercent > MAX_PRICE_CHANGE_PERCENT) return false;
        }
    }
    
    return true;
}

//==============================================
// TRADING STRUCTURES
//==============================================

struct TradeCommand {
    std::string command_id;
    std::string action;      // "BUY" or "SELL"
    std::string symbol;
    int quantity;
    double price;            // Optional for limit orders
    std::string order_type;  // "MARKET" or "LIMIT"
    
    TradeCommand() : quantity(0), price(0.0), order_type("MARKET") {}
};

bool parseTradeCommand(const std::string& jsonStr, TradeCommand& cmd) {
    // Reset command
    cmd.command_id = "";
    cmd.action = "";
    cmd.symbol = "";
    cmd.quantity = 0;
    cmd.price = 0.0;
    cmd.order_type = "MARKET";
    
    // Simple JSON parsing - extract command_id
    size_t pos = jsonStr.find("\"command_id\":");
    if (pos != std::string::npos) {
        size_t start = jsonStr.find('"', pos + 13);
        size_t end = jsonStr.find('"', start + 1);
        if (start != std::string::npos && end != std::string::npos) {
            cmd.command_id = jsonStr.substr(start + 1, end - start - 1);
        }
    }
    
    // Extract action
    pos = jsonStr.find("\"action\":");
    if (pos != std::string::npos) {
        size_t start = jsonStr.find('"', pos + 9);
        size_t end = jsonStr.find('"', start + 1);
        if (start != std::string::npos && end != std::string::npos) {
            cmd.action = jsonStr.substr(start + 1, end - start - 1);
        }
    }
    
    // Extract symbol
    pos = jsonStr.find("\"symbol\":");
    if (pos != std::string::npos) {
        size_t start = jsonStr.find('"', pos + 9);
        size_t end = jsonStr.find('"', start + 1);
        if (start != std::string::npos && end != std::string::npos) {
            cmd.symbol = jsonStr.substr(start + 1, end - start - 1);
        }
    }
    
    // Extract quantity
    pos = jsonStr.find("\"quantity\":");
    if (pos != std::string::npos) {
        pos += 11;
        while (pos < jsonStr.length() && (jsonStr[pos] == ' ' || jsonStr[pos] == ':')) pos++;
        cmd.quantity = atoi(jsonStr.substr(pos).c_str());
    }
    
    // Extract price (optional)
    pos = jsonStr.find("\"price\":");
    if (pos != std::string::npos) {
        pos += 8;
        while (pos < jsonStr.length() && (jsonStr[pos] == ' ' || jsonStr[pos] == ':')) pos++;
        cmd.price = atof(jsonStr.substr(pos).c_str());
    }
    
    // Extract order_type
    pos = jsonStr.find("\"order_type\":");
    if (pos != std::string::npos) {
        size_t start = jsonStr.find('"', pos + 13);
        size_t end = jsonStr.find('"', start + 1);
        if (start != std::string::npos && end != std::string::npos) {
            cmd.order_type = jsonStr.substr(start + 1, end - start - 1);
        }
    }
    
    return !cmd.command_id.empty() && !cmd.action.empty() && cmd.quantity > 0;
}

std::string createTradeResponse(const std::string& command_id, const std::string& status, 
                               const std::string& message, double fill_price = 0.0) {
    std::stringstream json;
    json.precision(8);
    json << std::fixed;
    
    json << "{";
    json << "\"command_id\":\"" << escapeJsonString(command_id) << "\",";
    json << "\"status\":\"" << escapeJsonString(status) << "\",";
    json << "\"message\":\"" << escapeJsonString(message) << "\",";
    if (fill_price > 0) {
        json << "\"fill_price\":" << fill_price << ",";
    } else {
        json << "\"fill_price\":null,";
    }
    json << "\"timestamp\":\"" << getCurrentTimestamp() << "\"";
    json << "}";
    
    return json.str();
}

int executeTrade(SCStudyInterfaceRef& sc, const TradeCommand& cmd, double& fillPrice) {
    // Log trade attempt for debugging
    std::stringstream logMsg;
    logMsg << "TRADE ATTEMPT: " << cmd.action << " " << cmd.quantity 
           << " Symbol: " << cmd.symbol << " Chart: " << sc.Symbol.GetChars();
    sc.AddMessageToLog(logMsg.str().c_str(), 0);
    
    // Check if trading is enabled for this study
    if (!sc.AllowEntryWithWorkingOrders) {
        sc.AddMessageToLog("TRADE REJECTED: AllowEntryWithWorkingOrders not enabled", 1);
        return 0;
    }
    
    // Check if we can submit orders to trade service
    if (!sc.SendOrdersToTradeService) {
        sc.AddMessageToLog("TRADE REJECTED: SendOrdersToTradeService not enabled", 1);
        return 0;
    }
    
    // Log current trading settings
    std::stringstream settingsMsg;
    settingsMsg << "Trading Settings: MaxPos=" << sc.MaximumPositionAllowed 
                << " SendToTrade=" << (sc.SendOrdersToTradeService ? "ON" : "OFF")
                << " AllowEntry=" << (sc.AllowEntryWithWorkingOrders ? "ON" : "OFF");
    sc.AddMessageToLog(settingsMsg.str().c_str(), 0);
    
    // Validate symbol matches current chart (case-insensitive)
    if (!cmd.symbol.empty()) {
        if (sc.Symbol.CompareNoCase(cmd.symbol.c_str()) != 0) {
            sc.AddMessageToLog("TRADE REJECTED: Symbol mismatch", 1);
            return 0;
        }
    }
    
    // Validate quantity
    if (cmd.quantity <= 0) {
        sc.AddMessageToLog("TRADE REJECTED: Invalid quantity <= 0", 1);
        return 0;
    }
    if (cmd.quantity > MAX_POSITION_SIZE) {
        sc.AddMessageToLog("TRADE REJECTED: Quantity exceeds maximum", 1);
        return 0;
    }
    
    // Validate market data availability
    if (sc.Ask <= 0 || sc.Bid <= 0) {
        sc.AddMessageToLog("TRADE REJECTED: No valid bid/ask data", 1);
        return 0;
    }
    
    // Create Sierra Chart order with proper initialization
    s_SCNewOrder order;
    memset(&order, 0, sizeof(order)); // Zero initialize all fields
    order.OrderQuantity = cmd.quantity;
    
    // Set order type
    if (cmd.order_type == "LIMIT" && cmd.price > 0) {
        order.OrderType = SCT_ORDERTYPE_LIMIT;
        order.Price1 = cmd.price;
        fillPrice = cmd.price;
        sc.AddMessageToLog("Using LIMIT order", 0);
    } else {
        order.OrderType = SCT_ORDERTYPE_MARKET;
        fillPrice = (cmd.action == "BUY") ? sc.Ask : sc.Bid;
        sc.AddMessageToLog("Using MARKET order", 0);
    }
    
    // Additional order settings for better execution
    order.TimeInForce = SCT_TIF_DAY; // Day order
    order.OrderType = SCT_ORDERTYPE_MARKET; // Force market order for reliability
    
    // Execute trade
    int result = 0;
    if (cmd.action == "BUY") {
        sc.AddMessageToLog("Executing BUY order...", 0);
        result = sc.BuyEntry(order);
        fillPrice = sc.Ask; // Use current ask for market buy
    } else if (cmd.action == "SELL") {
        sc.AddMessageToLog("Executing SELL order...", 0);
        result = sc.SellEntry(order);
        fillPrice = sc.Bid; // Use current bid for market sell
    }
    
    // Log execution result
    if (result > 0) {
        std::stringstream successMsg;
        successMsg << "TRADE ORDER PLACED: ID=" << result << " Price=" << fillPrice;
        sc.AddMessageToLog(successMsg.str().c_str(), 1);
    } else {
        sc.AddMessageToLog("TRADE ORDER FAILED: BuyEntry/SellEntry returned 0", 1);
    }
    
    return result;
}

//==============================================
// FILE OPERATIONS
//==============================================

bool writeMarketData(const std::string& jsonData) {
    try {
        // Ensure directory exists
        #ifdef _WIN32
        CreateDirectoryA("C:\\SierraChart", NULL);
        CreateDirectoryA("C:\\SierraChart\\Data", NULL);
        #endif
        
        // Try direct write first (simpler)
        std::ofstream file(MARKET_DATA_FILE, std::ios::out | std::ios::trunc);
        if (!file.is_open()) {
            // If direct write fails, try temp file approach
            std::string tempFile = std::string(MARKET_DATA_FILE) + ".tmp";
            std::ofstream tempFileStream(tempFile, std::ios::out | std::ios::trunc);
            if (!tempFileStream.is_open()) return false;
            
            tempFileStream << jsonData;
            tempFileStream.flush();
            tempFileStream.close();
            
            // Try to rename temp file to final file
            #ifdef _WIN32
            // On Windows, remove existing file first, then rename
            DeleteFileA(MARKET_DATA_FILE);
            return (MoveFileA(tempFile.c_str(), MARKET_DATA_FILE) != 0);
            #else
            return (rename(tempFile.c_str(), MARKET_DATA_FILE) == 0);
            #endif
        } else {
            // Direct write succeeded
            file << jsonData;
            file.flush();
            file.close();
            return true;
        }
        
    } catch (...) {
        return false;
    }
}

bool processTradeCommands(SCStudyInterfaceRef& sc) {
    try {
        std::ifstream file(TRADE_COMMANDS_FILE);
        if (!file.is_open()) return false;
        
        std::string line, content;
        while (std::getline(file, line)) {
            content += line;
        }
        file.close();
        
        if (!content.empty()) {
            // Remove command file immediately to prevent re-execution
            std::remove(TRADE_COMMANDS_FILE);
            
            // Parse and execute trade command
            TradeCommand cmd;
            if (parseTradeCommand(content, cmd)) {
                double fillPrice = 0.0;
                int orderId = executeTrade(sc, cmd, fillPrice);
                
                std::string response;
                if (orderId > 0) {
                    // Success
                    response = createTradeResponse(cmd.command_id, "FILLED", 
                                                 "Trade executed successfully", fillPrice);
                    
                    std::stringstream logMsg;
                    logMsg << "TRADE EXECUTED: " << cmd.action << " " << cmd.quantity 
                          << " " << cmd.symbol << " @ " << fillPrice;
                    sc.AddMessageToLog(logMsg.str().c_str(), 1);
                    
                } else {
                    // Failed
                    response = createTradeResponse(cmd.command_id, "REJECTED", 
                                                 "Trade execution failed");
                    sc.AddMessageToLog("TRADE REJECTED: Execution failed", 1);
                }
                
                // Write response file
                std::ofstream respFile(TRADE_RESPONSES_FILE, std::ios::out | std::ios::trunc);
                if (respFile.is_open()) {
                    respFile << response;
                    respFile.close();
                }
                
            } else {
                // Invalid command format
                std::string response = createTradeResponse("unknown", "REJECTED", 
                                                         "Invalid command format");
                std::ofstream respFile(TRADE_RESPONSES_FILE, std::ios::out | std::ios::trunc);
                if (respFile.is_open()) {
                    respFile << response;
                    respFile.close();
                }
                sc.AddMessageToLog("TRADE REJECTED: Invalid command format", 1);
            }
        }
        
        return true;
    } catch (...) {
        return false;
    }
}

//==============================================
// STUDY STATE
//==============================================

struct StudyState {
    bool initialized;
    DWORD lastUpdate;
    DWORD lastTradeCheck;
    int packetsWritten;
    int validationErrors;
    int tradesExecuted;
    DWORD startTime;
    bool tradingEnabled;
    
    StudyState() : initialized(false), lastUpdate(0), lastTradeCheck(0), 
                   packetsWritten(0), validationErrors(0), tradesExecuted(0),
                   startTime(0), tradingEnabled(false) {}
};

//==============================================
// MAIN STUDY FUNCTION
//==============================================

SCSFExport scsf_MinhOSBridgeStudy(SCStudyInterfaceRef sc) {
    static StudyState state;
    
    // Study setup
    if (sc.SetDefaults) {
        sc.GraphName = "MinhOS Bridge";
        sc.StudyDescription = "Complete market data and trading bridge for MinhOS v3. "
                             "Exports market data and executes trades via JSON file communication. "
                             "Bridge runs on port 8765 for Linux client connection.";
        
        sc.AutoLoop = 1;
        sc.GraphRegion = 0;
        sc.FreeDLL = 1;
        
        // Enable trading capabilities
        sc.AllowMultipleEntriesInSameDirection = false;
        sc.MaximumPositionAllowed = MAX_POSITION_SIZE;
        sc.SupportReversals = true;
        sc.SendOrdersToTradeService = true;
        sc.AllowOppositeEntryWithOpposingPositionOrOrders = true;
        sc.SupportAttachedOrdersForTrading = true;
        sc.UseGUIAttachedOrderSetting = false;
        sc.CancelAllOrdersOnEntriesAndReversals = true;
        sc.AllowEntryWithWorkingOrders = true;
        sc.SupportTradingScaleIn = false;
        sc.SupportTradingScaleOut = false;
        
        // Study inputs
        sc.Input[0].Name = "Update Interval (ms)";
        sc.Input[0].SetInt(1000);
        sc.Input[0].SetIntLimits(100, 10000);
        
        sc.Input[1].Name = "Enable Logging";
        sc.Input[1].SetYesNo(1);
        
        sc.Input[2].Name = "Enable Trading";
        sc.Input[2].SetYesNo(0);  // Default OFF for safety
        
        sc.Input[3].Name = "Trade Check Interval (ms)";
        sc.Input[3].SetInt(500);
        sc.Input[3].SetIntLimits(100, 5000);
        
        return;
    }
    
    // Initialize once
    if (!state.initialized) {
        state.startTime = GetTickCount();
        state.tradingEnabled = sc.Input[2].GetYesNo();
        state.initialized = true;
        
        if (sc.Input[1].GetYesNo()) {
            sc.AddMessageToLog("MinhOS Bridge Study Started", 1);
            sc.AddMessageToLog("Market data: C:/SierraChart/Data/minhos_market_data.json", 1);
            sc.AddMessageToLog("Trade commands: C:/SierraChart/Data/minhos_trade_commands.json", 1);
            sc.AddMessageToLog("Trade responses: C:/SierraChart/Data/minhos_trade_responses.json", 1);
            sc.AddMessageToLog("Bridge URL: http://localhost:8765", 1);
            
            if (state.tradingEnabled) {
                sc.AddMessageToLog("TRADING ENABLED - Ready to execute trades", 1);
            } else {
                sc.AddMessageToLog("TRADING DISABLED - Market data only mode", 1);
            }
        }
    }
    
    // Skip if insufficient data
    if (sc.Index < 1) return;
    
    // Only process on new real-time data
    if (sc.Index != sc.ArraySize - 1) return;
    
    DWORD currentTime = GetTickCount();
    int updateInterval = sc.Input[0].GetInt();
    int tradeCheckInterval = sc.Input[3].GetInt();
    
    // Update dynamic settings
    state.tradingEnabled = sc.Input[2].GetYesNo();
    
    // Send market data
    if (currentTime - state.lastUpdate >= (DWORD)updateInterval) {
        state.lastUpdate = currentTime;
        
        // Validate data
        if (!isValidData(sc)) {
            state.validationErrors++;
            if (sc.Input[1].GetYesNo()) {
                sc.AddMessageToLog("Invalid data detected - skipping", 0);
            }
            return;
        }
        
        // Create and write market data
        std::string jsonData = createBridgeMarketDataJSON(sc);
        
        if (writeMarketData(jsonData)) {
            state.packetsWritten++;
            
            // Log success periodically
            if (sc.Input[1].GetYesNo() && (state.packetsWritten % 60 == 0)) {
                std::stringstream msg;
                msg << "Bridge data packets: " << state.packetsWritten 
                    << ", Trades: " << state.tradesExecuted
                    << ", Errors: " << state.validationErrors;
                sc.AddMessageToLog(msg.str().c_str(), 0);
            }
        } else {
            if (sc.Input[1].GetYesNo()) {
                sc.AddMessageToLog("ERROR: Failed to write market data file", 1);
            }
        }
    }
    
    // Process trade commands
    if (state.tradingEnabled && currentTime - state.lastTradeCheck >= (DWORD)tradeCheckInterval) {
        state.lastTradeCheck = currentTime;
        
        if (processTradeCommands(sc)) {
            state.tradesExecuted++; // Increment on successful processing
        }
    }
    
    // Display comprehensive status
    DWORD uptimeSeconds = (currentTime - state.startTime) / 1000;
    
    std::stringstream status;
    status << "MinhOS Bridge: " << state.packetsWritten << " data";
    
    if (state.tradingEnabled) {
        status << " | " << state.tradesExecuted << " trades | TRADING ON";
        
        // Show current position
        s_SCPositionData posData;
        sc.GetTradePosition(posData);
        if (posData.PositionQuantity != 0) {
            status << " | Pos:" << posData.PositionQuantity 
                   << " P&L:$" << (int)posData.OpenProfitLoss;
        }
    } else {
        status << " | TRADING OFF";
    }
    
    status << " | " << uptimeSeconds << "s";
    
    if (state.validationErrors > 0) {
        status << " | " << state.validationErrors << " err";
    }
    
    // Add status text to chart
    s_UseTool tool;
    tool.ChartNumber = sc.ChartNumber;
    tool.DrawingType = DRAWING_TEXT;
    tool.Region = 0;
    tool.Color = state.tradingEnabled ? RGB(0, 255, 0) : RGB(255, 165, 0); // Green if trading, orange if not
    tool.FontSize = 10;
    tool.FontBold = 1;
    tool.BeginValue = sc.High[sc.Index] * 1.01f;
    tool.BeginDateTime = sc.DateTimeOut[sc.Index];
    tool.Text = status.str().c_str();
    tool.LineNumber = 9999; // High number to avoid conflicts
    sc.UseTool(tool);
}