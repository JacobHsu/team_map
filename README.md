# MLB 球隊位置互動儀表板

這是一個結合地圖視覺化和即時比分的 MLB 球隊互動儀表板，展示所有 30 支 MLB 球隊的地理位置，並整合 Sportradar Score Ticker 顯示即時比賽資訊。

![Image](https://github.com/user-attachments/assets/50584814-8195-4565-9b2d-35266cd9cb77)

## 功能特色

- 🗺️ **互動式地圖**：顯示所有 MLB 球隊的地理位置
- 📊 **即時比分**：整合 Sportradar Score Ticker 顯示 MLB 比賽即時資訊
- 🏟️ **球隊資訊**：點擊球隊可查看詳細資訊和位置
- 📱 **響應式設計**：適應不同螢幕尺寸


## ✨ 主要功能 (Features)

*   **專業三欄式儀表板設計**
    *   將「美國聯盟」與「國家聯盟」圖例分置於左右兩側，中間為核心地圖，資訊一目了然。
    *   版面自動適應視窗大小，實現無滾動的「一頁式」瀏覽體驗。

*   **全功能互動地圖**
    *   **地圖操作**：使用者可自由拖曳、縮放地圖。
    *   **球隊 LOGO 標記**：使用各隊官方 LOGO 精準標示於地圖上。
    *   **豐富的懸停資訊卡**：滑鼠懸停在地圖 LOGO 上，會顯示包含城市、州名、完整隊名（中/英）及縮寫的詳細資訊卡。
    *   **一鍵恢復視圖**：地圖左上角提供「Home」按鈕，可隨時將視圖平滑移回預設的全美地圖。

*   **智慧連動圖例**
    *   **清晰分類**：左右圖例嚴格按照「聯盟 (AL/NL)」及「分區 (東/中/西)」進行歸類。
    *   **點擊連動**：點擊圖例中的任一球隊，地圖會自動飛行並聚焦至該隊位置，同時彈出其詳細資訊卡。
    *   **詳細資訊**：每個圖例項目均包含 LOGO、中文隊名、英文隊名及球隊縮寫。

*   **精緻的視覺與風格**
    *   **單一檔案**：所有功能（HTML, CSS, JavaScript）都整合在一個檔案中，極度輕便。
    *   **專業字體**：引入 Google Fonts 的 "Roboto" 字體，打造類似官方網站的專業、清晰視覺感。
    *   **繁體中文介面**：所有圖示說明與提示文字皆為繁體中文，符合在地化需求。
    *   **穩定資源**：所有球隊 LOGO 及地圖圖資均來自穩定的 CDN 服務，確保長期可用性。

## 🚀 如何使用 (How to Use)

1.  **下載檔案**：取得專案中的 `index.html` 檔案。
2.  **用瀏覽器開啟**：直接在您的電腦上用任何現代網頁瀏覽器（如 Google Chrome, Firefox, Microsoft Edge）開啟此 `index.html` 檔案即可。
    *   不需要安裝任何網頁伺服器（如 Apache, Nginx）。

## 📁 檔案結構 (File Structure)

本專案的所有程式碼都包含在單一的 `index.html` 檔案中，其內部結構如下：

*   **`<head>`**：
    *   引入 **Leaflet.js** 的 CSS 樣式表。
    *   引入 **Google Fonts (Roboto)** 的字體檔案。
*   **`<style>`**：
    *   包含了所有自訂的 CSS 程式碼，負責儀表板的三欄式佈局、顏色、字體、按鈕及提示框的樣式。
*   **`<body>`**：
    *   定義了儀表板的 HTML 骨架，包括標題、左右側邊欄（圖例區）及中間的地圖容器。
*   **`<script>`**：
    *   引入 **Leaflet.js** 的核心函式庫。
    *   包含專案所有的 JavaScript 邏輯：
        *   `teams` 陣列：儲存所有球隊的完整資料。
        *   地圖初始化與設定。
        *   動態生成地圖標記（Markers）與圖例項目。
        *   處理所有互動事件（滑鼠懸停、圖例點擊、恢復視圖按鈕）。

## 🛠️ 技術棧 (Technologies Used)

*   **HTML5**
*   **CSS3** (特別是 Flexbox 用於版面佈局)
*   **JavaScript (ES6)**
*   **[Leaflet.js](https://leafletjs.com/)**：一個輕量、高效的開源互動地圖函式庫。
*   **[CARTO](https://carto.com/)**：提供簡潔、專業的淺色系地圖圖資。
*   **[Google Fonts](https://fonts.google.com/)**：提供高品質的 "Roboto" 網頁字體。
*   **[ESPN CDN](https://a.espncdn.com/)**：提供穩定、可靠的球隊 LOGO 圖片來源。

[Google AI Studio](https://aistudio.google.com/prompts/new_chat)  
啟用 `Grounding with Google Search` 


### 提示詞

請幫我建立一個單一 HTML 檔案，內容是一個 MLB 球隊位置的互動式儀表板。

**一、 整體版面配置：**

*   採用專業的全螢幕三欄式儀表板（Dashboard）版面配置，頁面無需垂直捲動。
*   **左側欄：** 顯示完整的「美國聯盟」球隊圖例。
*   **中間區塊：** 顯示「互動式美國地圖」。
*   **右側欄：** 顯示完整的「國家聯盟」球隊圖例。

**二、 中間地圖功能：**

1.  **地圖標記：** 使用各隊的官方 LOGO 作為地圖上的位置標記（請務必使用穩定、有效的圖片 CDN 來源，以避免圖片失效）。
2.  **滑鼠懸停效果：** 當滑鼠懸停在地圖上的任一 LOGO 時，應彈出一個格式化的資訊卡，清晰顯示該隊的【城市與州名】、【中文隊名】、【英文隊名】及【球隊縮寫】。
3.  **恢復視圖按鈕：** 地圖左上角需有一個「恢復預設視圖」的按鈕（例如房屋圖示）。點擊後，地圖會平滑地飛回初始的全美視圖，並關閉任何已彈出的資訊卡。

**三、 左右圖例功能：**

1.  **分類結構：** 左右側的圖例需在各自聯盟下，再依照【東區】、【中區】、【西區】進行明確的分類。
2.  **項目內容：** 每個圖例項目應包含【LOGO】、【中文隊名】、【英文隊名】及【球隊縮寫】。
3.  **點擊互動：** 圖例中的每一個球隊項目都必須可以點擊。點擊後，地圖會以平滑動畫飛行（flyTo）並縮放到該球隊的位置，同時自動彈出與滑鼠懸停時效果相同的詳細資訊卡。

**四、 整體風格與語言：**

1.  **語言：** 所有使用者可見的文字，包括標題、圖例和提示資訊，都需使用**繁體中文**。
2.  **視覺風格：** 整體風格需簡潔、專業。請引入與 MLB 官網風格相似的清晰、現代字體（例如 Google Fonts 的 Roboto）。圖例中的英文與縮寫文字需清晰、易讀，字體大小適中且顏色要夠深，以確保閱讀體驗。


## Sportradar Score Ticker 

### 參考來源


- [Score Ticker](https://widgets.media.sportradar.com/usdemo#eyJzcG9ydCI6Im1sYiIsImNhdGVnb3J5IjoibGVhZ3VlIiwic2Vhc29uSWQiOjEyNTczNSwibWF0Y2hJZCI6NTUzMDkxODMsInRlYW1VaWQiOjU5MzAsInBsYXllcklkIjo4NjUxMDYsInBsYXllcklkcyI6WzE0ODczMjAsODQzMzMzLDg2NDIwOCwyMTM5NjA4LDE3NDUyMDUsODQzODY3LDg0OTE2MCwxNjkyNTYzLDEwNzk5MzgsMTM1ODQ3NCwxNTM5NzY5LDg0ODU2NywyMTQ2NTU0LDg2NTEwNiwxNjk0MzEzLDI1NTAyNzMsMTA3ODEyMiwxNTM1MjM1LDExMzQxNzksODQyNjk1LDE1MzkxODksMTc0OTk1Myw4NDE3NTcsMTM5OTU5MywyMzI0MzUxLDEwOTgxMjBdfQ==)
- [Widgets Introduction](https://developer.sportradar.com/widgets/docs/getting-started)  
- [Widgets.us.common.ScoreTicker](https://widgets.media.sportradar.com/usdocs/Widgets.us.common.ScoreTicker.html)  
- [Score Ticker](https://developer.sportradar.com/widgets/docs/nfl-score-ticker)  

### 實作方法

**HTML 聲明式（推薦）**

在 `<head>` 中載入：
```html
<script type="application/javascript"
        src="https://widgets.media.sportradar.com/uscommon/widgetloader"
        data-sr-language="en_us" async>
</script>
```

在 `<body>` 中放置：
```html
<div class="sr-widget"
     data-sr-widget="us.common.scoreTicker"
     data-sr-sport="mlb">
</div>
```
