# Sierra Chart Settings Configuration

## Data/Trade Service Settings
- **Current Selected Service**: SC Data [data]
- **DTS Config**: Load/Save/Delete buttons available

## General Settings

### Chartbook Tabs
- **Use Chartbook Tabs**: Yes
- **Show Chartbook Tabs At**: Top
- **Support Multiple Rows For Chartbook Tabs**: No
- **Show Arrows Before Chartbook Tabs**: No

### Window Tabs
- **Use MDI Window Tabs**: Yes
- **Show MDI Window Tabs At**: Bottom
- **Support Multiple Rows For MDI Tabs**: No
- **Show Arrows Before MDI Tabs**: No

### Window Tiling
- **Use Windows Custom Grid Layout**: No
- **Rows Count**: 0
- **Columns Count**: 0

### Scroll
- **Scroll Multiplier**: 1.00
- **Enable Workspace Scrolling**: No
- **Scroll Wheel**: Scroll Wheel Scrolls Chart. With 'Shift' Changes Spacing

### Application GUI
- **Custom Title Bar Name**: [empty]
- **Auto Hide Charts Title Bar And Scrollbar**: No
- **Minimize / Restore Detached Windows With Main Window**: No
- **Bring Detached Windows to Top on Main Window Focus**: No
- **Ignore Minimized Windows When Tiling**: No
- **Destroy Chart Windows When Hidden**: No
- **Use Alternate Window Placement Method (Restart required)**: No
- **Status Bar Width in Characters**: 30
- **Small Pixel Amount Scaling Factor**: 1
- **Display Save All Option on Exit**: Yes
- **Disable Prompt to Save Chartbook on Chartbook Close**: No

### Menu Settings
- **Sort CW Menu by Chart Number**: No
- **Maximum Items per Column for CW Menu**: 30
- **Maximum Items per Column for Study Collections Menu**: 30

### Printing
- **Print Only In Black And White**: No

### Charts
- **Hide Study Inputs On Charts**: No
- **Color Chart Tabs with Chart Link Number Color**: No
- **Display Chart Timeframe On Tabs When Title Bar Name Is Set To Be Used On Chart Tab**: No
- **Show Chart Number First on Chart Name**: No
- **Show On-Chart Status Messages**: Yes
- **Use Controlled Order Chart Updating**: No
- **Large Increase/Decrease Chart Spacing Pixels**: 5
- **Interactive Scale Range Movement Adjust Direction**: Move down decreases range. Move up increases range.
- **Interactive Scale Range Percent Change for Full Region Move**: 1
- **Display Fractions In Short Format**: No
- **Allow New Data In Unlocked Fill Space**: Yes
- **Additional Days to Add to Rollover Date for Chart and Quote Board Rollovers**: 0
- **Reset Bar Size/Spacing/Scale On Symbol Change**: No
- **Reset Bar Size/Spacing/Scale On Timeframe Change**: No

### Study Collection
- **Use Default Study Collection for New Charts**: No
- **Default Study Collection**: [empty]

### Symbol
- **Support Plus Minus Keys for Changing Symbol in Charts**: Yes
- **Support Symbol Entry from Chart Window**: No
- **Support Bar Period Keyboard Entry from Chart**: Yes
- **Detect Rollover Of Current Futures Contracts Symbols Based On Real Time Volume**: Yes

### Chartbooks
- **Close Existing Chartbooks When Open Chartbook Group**: Yes
- **Auto-Save Chartbooks**: No
- **Auto-Save Chartbooks Interval in Minutes**: 30

### Files And Folder Paths
- **Data Files Folder**: C:\SierraChart\Data
- **Always Use 'Data' Folder Within Main Folder**: Yes
- **Chart Image Folder**: C:\SierraChart\Images\
- **Text Editor Path and Filename**: C:\SierraChart\NPP\notepad++.exe
- **Market Depth Data Path**: C:\SierraChart\Data\MarketDepthData\
- **Web Browser Path and Filename**: [empty]
- **Trade Activity Logs Folder Path**: [empty]
- **Chat Data History Folder Path**: [empty]
- **Advanced Custom Study Editor Path**: C:\SierraChart\NPP\notepad++.exe

## Alert Settings

### Alert 1 Configuration
- **Alert Number**: Alert 1
- **Number of Times to Play This Alert**: 1
- **Do Not Play Alert Sound**: No
- **Run Program when this Alert Triggered**: [empty]
- **Text to Play when this Alert Triggered**: [empty]
- **Send Alert as Chat Message when this Alert is Triggered (External alerts)**: No
- **Chat Identifier for Alert**: 0
- **Capture Chart Image on Alert for Chart**: No
- **Capture Chart Image on Trade Order Event**: No
- **Include Alert Comment in Alert ChatMessage/Popup**: Yes
- **Add Alert To Compact Alert Pop-up Window**: No

### Sound File
- **Alert Sound File Name**: AlertSound.wav

### User Defined Name
- **User Defined Name**: [empty]
- **Include User Defined Name in Alert ChatMessage/Popup**: Yes
- **Use User Defined Name Only in Alert Message**: No

### Notification
- **Chat Identifier or Chat Name for Alerts**: [empty]

### Additional Settings
- **Show Alerts Log On Study Alert**: No
- **Wait for Prior Alert Sound to Finish before Playing Next Queued Sound**: Yes

### Remote Alerts
- **Enable Remote Alerts**: No
- **Alert Number for Remote Alert**: No Alert Sound

### Other Alerts
- **Server Connected Alert**: No Alert Sound
- **Server Connection Lost Alert**: No Alert Sound
- **Chat Window New Message Alert**: No Alert Sound
- **Chat Window Pending Messages Alert**: No Alert Sound
- **Chat Window Edited Message Alert**: No Alert Sound
- **Chat Window Message Read Alert**: No Alert Sound
- **Chat Offline Alert**: No Alert Sound

### Text To Speech Wave File Creation
- **Text To Speech Wave File Name**: Enter up to 20 word phrase

## NTP Client Settings
- **NTP Client Enable**: No
- **NTP Client working Status**: [empty]
- **NTP Servers**: [empty]
- **Individual Server Polling Interval (Seconds)**: 60
- **Number of Responses to Wait for to Update Time**: 4
- **Minimum Number of Responses to Wait for to Update Time**: 2
- **Time Delay After Last Received Response to Update Time if Insufficient Responses (Seconds)**: 10
- **Threshold Level in Milliseconds for Increasing/Decreasing Polling Interval**: 5
- **Number of Clock Adjustments to Determine Automatic Adjustment**: 5
- **Last Offset Value**: [empty]
- **Peers Info**: [empty]
- **Has Privilege to set System time**: No

## Sierra Chart Server Settings

### General
- **Detailed Heartbeat Logging**: No
- **Use Port 80 For Historical Data (Not Recommended)**: No
- **Always Use Port 443 For Real-Time Data**: No
- **UDP Port (0 = not used)**: 0
- **Use Encryption for Historical Data Downloads**: No
- **Max Depth Levels**: 100
- **Support Downloading Historical Market Depth Data**: Yes
- **Max Historical Market Depth Days to Download**: 5
- **Subscribe Market By Order Data When Market Depth Subscribe**: No
- **Use Separate Connection For Market By Order Data**: Yes
- **Use Real-Time Data Compression**: Standard Compression
- **Remote Buffer Delay Send Time in Milliseconds**: 0
- **Max Historical Order Fills Days To Download**: 124

### Historical Data Client
- **Timeout in Seconds**: 90
- **Number of Retries After Timeout**: 2
- **Log Historical Price Data Fields in DTC HD Service Client**: No

### Special
- **Use Internal LAN IP for CME Data and Order Routing**: No
- **Use Single Network Receive Buffer for Linux Compatibility**: No
- **CME Exchange Data Feed Server Address and Port Override**: [empty]
- **CME Exchange Data Feed Historical Server Address Override**: [empty]
- **Standard Sierra Chart Server Address Override (non-exchange/no-fee data)**: [empty]

### Network Socket
- **Network Socket Connection Timeout Time In Seconds**: 24

### DTC Protocol Server
- **Enable DTC Protocol Server**: Yes
- **Use Delayed Sends**: No
- **Listening Port**: 11099
- **Additional Listening Port**: 0
- **DTC Protocol Server is Listening**: Yes
- **Historical Data Port**: 11098
- **DTC Protocol Clients**: 0
- **Historical Data Clients**: 0
- **Interprocess Synchronization Servers**: 0
- **Access All Trade Accounts Individual Servers**: 0
- **Auto Send Security Definition For New Symbols**: No
- **Allow Trading**: Yes
- **Require Authentication**: No
- **Require TLS**: No
- **Automatically use JSON Compact Encoding for Websocket Connections**: Yes
- **Encoding**: Automatic
- **Allowed Incoming IPs**: Local Computer Only
- **TLS Historical Data Port**: 0
- **Enable JSON Logging**: No
- **Network Socket Delayed Send Interval in milliseconds**: 0

## Chart Trade Settings

### Working Orders - Display
- **Order Quantity**: Yes
- **Order Price**: Yes
- **Stop-Limit Order Limit Price**: Yes
- **Order Type**: Yes
- **Additional Order Information**: No
- **Order Status**: Yes
- **Attached Order P/L When Modifying**: No
- **Filled Quantity**: Yes
- **Attached Order P/L Always**: No
- **Buy/Sell**: No
- **Estimated Position (Q)**: No
- **Order Association Lines**: No
- **Limit Line for Stop-Limit Orders**: No
- **Single Character Order Type Names**: No
- **Number of Decimal Places for Fractional Order Quantities**: 0
- **Allow Order Quantity on Order Line To Be Changeable**: Yes

### Order Entry
- **Use Click, Release, Click Method to Adjust Orders**: No
- **Reject Stop Orders That Will Immediately Fill**: No
- **Reject Chart Trade Orders That Will Immediately Fill**: No
- **Adjust Trail Offset When Modifying Trail Order**: No
- **Require Full Fill of Target For Move to Breakeven Attached Order**: No
- **Display Chart Trade Commands As Sub-Menu**: No
- **Display Chart Trade Commands On Chart Drawing Context Menu**: Yes
- **Move to Breakeven (BE) Command**: Move Nearest Stop Attached Order
- **Always Use Position Average for Reference Price for Break Even Command**: No
- **Use Current Price for Autoset OCO Chart Orders**: No
- **Support Scale in with Pending Attached Orders Only**: No
- **Allow Adjust First Price for OCO Order Entry**: No

### Order Modifications
- **Maintain Same Offset Between Target and Stop Attached Orders**: No
- **Move Attached Targets/Stops to Price Also Moves OCO**: No

### Chart Position Line
- **Coloring Of Position Line Based On**: Profit/Loss
- **Display Profit/Loss On Position Line**: Yes
- **Display Average Price**: Yes

### Display Trade Window Controls
- **Buy Market**: Yes
- **Buy Ask**: Yes
- **Buy Bid**: Yes
- **Sell Market**: Yes
- **Sell Ask**: Yes
- **Sell Bid**: Yes
- **Flatten**: Yes
- **Reverse**: Yes
- **Cancel All**: Yes

### Other
- **Display Daily Profit/Loss On Chart/Trade DOM**: Yes
- **Include Open P/L in Chart/Trade DOM P/L Display (NPL)**: No
- **Show Limit/Stop in Trade Mode Box**: No
- **Display Trade Account on Chart/Trade DOM**: No

### Confirmations
- **Disable Order Confirmations - Global**: No

### Position in Queue
- **Enable Estimated Position in Queue Tracking**: No

### Order Fills
- **Display Fill Text**: Yes
- **Display Trade Profit/Loss**: No
- **Display Order Type**: No
- **Display Price**: Yes
- **Display Note**: No
- **Display Position Quantity**: No
- **Display Buy Fills**: Below Price
- **Display Sell Fills**: Above Price
- **Fill Marker Size**: 10
- **Display Entry/Exit Connecting Lines**: No
- **Color Connecting Lines Based On Profit/Loss**: No

## General Trade Settings

### General
- **Select Non-Sim Account on Entering Non-Sim Mode in SubInstances**: Yes
- **Common Profit/Loss Currency**: NONE
- **Number Decimal Places For Displayed Currency Value**: 2
- **Auto-Send Market Order On Rejected Stop Attached Order**: No

### Order Management
- **Adjust Attached Orders to Maintain Same Offset on Parent Fill**: Yes
- **Adjust Attached Orders to Maintain Same Offset on Parent Modification**: Yes
- **Cancel Pending Attached Orders Immediately Upon Parent Cancel Request for DTC Server**: Yes

### Server Side Orders
- **Use Server Side OCO Orders (if supported)**: Yes
- **Use Server Side Bracket Orders (if supported)**: No
- **Use Bid/Ask for Open P/L Calculations**: No
- **Hold Market Order Until Pending Cancel Orders Are Confirmed**: No

### Simulated Orders
- **Allow Simulated Resting Limit Order to Fill at Better Price**: Yes
- **Simulated Orders: Use Last Trade Price for Fill When Bid Ask Beyond Last Trade Price**: No
- **Reactivate Attached Order when Rejected Modification During Fill**: No
- **Number of Simulation Accounts**: 2
- **Disable Order Allocation To Trade Accounts On Chartbook Opening**: Yes

### Live Account Risk Manager Settings
- **Risk Manager Operator ID String Override**: [empty]
- **Risk Manager Sender Location ID String Override**: No Sender Location ID
- **Use Risk Manager Mode**: No

### Trade Activity
- **Automatically Delete Trade Activity Log Files on Startup Older than Days (>=2 is enabled)**: 0

### Scale In/Out
- **Scale In**: Furthest Orders
- **Scale Out**: Furthest Orders
- **Perform Immediate Scale Out with Market Order**: No
- **Perform Immediate Scale Out with Limit Order**: No
- **Support Scale Out Without Existing Position**: No

## Advanced Service Settings

### Reconnect
- **Reconnect Daily**: No
- **Reconnect Time**: 00:00:00
- **Reconnect Time Zone**: UTC (+0 UTC)
- **Reconnect Only On Sunday**: No
- **Reconnect Delay in Milliseconds**: 0

### Other
- **Intraday File Flush Time in Milliseconds (0=default)**: 0
- **Translate Symbols Automatically in Chartbooks and Quote Boards**: No

### File Compression
- **Support Intraday and Market Depth Files Compression**: Yes
- **Disable Intraday and Market Depth File Compression if Enabled on the File**: No

### Crash Reporter
- **Write Crash Dump and Terminate on Not Responsive Primary Thread**: No
- **Non-responsive time in seconds**: 180

## Intraday Data File Management
- **Auto Compress Every Days**: Unchecked
- **Delay Between Processing Records Batch in MS**: 0
- **Compress Records Older Than**: 180 Days
- **Compress To Data Unit Size**: 4 Seconds
- **Delete Any Previous Temporary Files Before Starting Compression**: Unchecked
- **Last Compression**: Never

## Message Categories Settings
All message categories are set to **No**:
- Unset, Error, Chartbook Sharing Error, Chartbook Sharing Info
- NTP Info, Historical Data, Data Feeds, Chat, External Service
- ACSIL, System, HTTP Communication, Network, Chart
- Symbol Settings, Trading, File System, Study, Chat Debug, Graphics

## Chart Studies Configuration (NQU25-CME[M] 1 Min)

### Active Studies
1. **Current Price Line**: ID:2 | 0 ms | CalcOrder: 1 | S_ID: 123
2. **Volume**: ID:3 | 0 ms | CalcOrder: 2 | S_ID: 8
3. **MinhOS Tick Data Exporter v3 - Final**: ID:1 | 0 ms | CalcOrder: 3

### Available Studies (Partial List)
- TRIX
- True Bar Average
- True Range
- True Strength Index
- Turbo MACD
- Ultimate Oscillator
- Up/Down Volume Difference Bars
- Up/Down Volume Ratio
- UpTick Volume
- Value Chart
- Value Chart Levels
- Vertical Horizontal Filter
- Volatility - Chaikin's
- Volatility - Historical
- Volatility Trend Indicator
- Volume (selected)

### Study Collection Options
- **Save Studies As Study Collection**: Available with name field
- **Save Single** / **Load** / **Delete** / **Save All** options
- **Prompt to Remove Existing Studies**: Available

## Settings Windows Configuration

### Window Behavior
- **Resize Settings Window on Column Count Change**: Yes
- **Fix Minimum Resize Limit**: No

### Single Click Settings
- **Use Single Click for Yes/No in Settings Window when not Selected**: No
- **Use Single Click for Edit Control in Settings Window when not Selected**: Yes
- **Use Single Click for List Box in Settings Window when not Selected**: Yes
- **Use Single Click for Editable List Box in Settings Window when not Selected**: Yes
- **Use Single Click for Button in Settings Window when not Selected**: Yes
- **Use Single Click for Color Control in Settings Window when not Selected**: No
- **Use Single Click for Font Control in Settings Window when not Selected**: Yes

### Edit Control Behavior
- **Select All Text in Edit Control Upon Editing**: No
- **Immediately Show Drop Down When List Setting Is Being Edited**: Yes
- **Immediately Show Drop Down When List Setting Is Being Edited (Chart Drawings/Tools)**: Yes
- **Show View Menu In Settings Window**: Yes
- **Use Mouse Scroll Wheel to Select Settings in Settings Window**: No
- **Scroll Wheel Up Selects Next Setting**: No
- **Edit Control with +/- Button Support +/- Keys When Selected and Not Editing**: No

### Search Configuration
- **Select String Matching Method in Search**: Exact String Matching

## Data/Trade Service Settings - Common Settings

### Connection Settings
- **Connect on Program Startup**: Yes
- **Reconnect on Failure**: Yes

### Data Storage
- **Intraday Data Storage Time Unit**: 1 Tick

### Historical Data Download Limits
- **Non-Tick Data**: 186 days
- **1-Tick Data**: 186 days
- **Formula Symbols**: 15 days

### Data Feed Settings
- **Allow Support for Sierra Chart Data Feeds**: Yes
- **Number of Stored Time and Sales Records**: 5000
- **Maximum Time and Sales Depth Levels**: 20
- **Enable FIX Logging**: Yes
- **Process Known Odd Lot Equity Trades for DTC Services**: Yes

### Historical Daily Data
- **Historical Daily Data Download Time**: 17:50:00
- **Historical Daily Equities Data Download Time**: 20:15:00
- **Historical Daily Data Download Time Zone**: New York (-5 EST/-4 EDT)
- **Download Dividend Adjusted Historical Equities Data**: No
- **Download Total Volume for All Contracts for Futures Daily Data**: Yes
- **Maximum Historical Days To Download For Daily Data**: 36500

## General Trade Settings - Notifications

### Trade Window Alerts
- **Open Trade Orders Window When Order Is Completed**: No
- **Open Trade Orders Window When Order Is Filled**: No

### Order Alert Sounds
- **Play Alert for New Order**: No Alert Sound
- **Play Alert When Order Filled (Others)**: No Alert Sound
- **Play Alert When Order Canceled**: No Alert Sound
- **Play Alert When Order Rejected**: No Alert Sound
- **Play Alert When Target Filled**: No Alert Sound
- **Play Alert When Stop Filled**: No Alert Sound

### Trade Order Management
- **Trade Order Alert Trade Accounts Filter**: [empty]
- **Display Confirmation for Order Cancellations from the 'Orders' Tab**: Yes
- **Open the Trade Service Log When a New Message is Added**: No
- **Skip Trade Order Alert if Within N Seconds of Previous Trade Order Alert Type**: 0

## General Settings - Log

### File Logging
- **Save Message Log To File**: No
- **Detailed Continuous Futures Contract Chart Logging**: No
- **Never Automatically Open Message Log or Trade Service Log**: No
- **Save Alerts Log to File**: No
- **Enable Detailed HTTP Logging**: No
- **Control Bar Debug Logging**: No
- **Window and List Box Debug Logging**: No

### Display Settings
- **Disable Visible Message Logging**: No
- **Display Grid for Message Logs**: No

## Study Settings: MinhOS Tick Data Exporter v3

### Graph Configuration
- **Graph Draw Type**: Custom
- **Use Chart Graphics Settings For Subgraph Colors**: No

### Subgraphs
1. **Tick Export Status (SG1)**
   - **Draw Style**: Line
   - **Line Style**: Solid
   - **Width**: 1
   - **Line Label**: -

2. **Processing Latency (μs) (SG2)**
   - **Draw Style**: Line
   - **Line Style**: Solid
   - **Width**: 1
   - **Line Label**: -

### Display Settings
- **Color**: Blue (for Tick Export Status)
- **Draw Style**: Line
- **Line Style**: Solid
- **Width/Size**: 1
- **Auto-Coloring**: None
- **Label**: Include in Summary
- **Short Name**: [empty]

### Study Options
- **Display Name and Value in Chart Values Windows**: Yes
- **Include in DataSheet**: Yes
- **Display Study Subgraphs Name and Value - Global**: Yes
- **Display Input Values**: Yes
- **Always Show Name and Value Labels When Enabled**: Yes
- **Display Name and Value in Region Data Line**: Yes
- **Use Transparent Label Background**: Yes
- **Use Common Displacement**: No
- **Resolve Full Names for Reference Inputs**: No
- **Display Values When Hidden**: No
- **Display Study Name**: Yes
- **Transparency Level for Fill Styles**: 75