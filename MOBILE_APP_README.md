# Axiom IPO Intelligence - Mobile App

A React Native mobile application for analyzing IPOs using evidence-driven scoring and historical validation.

## Features

### Core Functionality
- **IPO Analysis** — Enter company data to receive trade and investment scores
- **Historical Backtest** — Test scores against 14 real historical IPOs
- **Watchlist** — Save IPOs for tracking and comparison
- **Analysis History** — Keep all your analyses with timestamps
- **Share Results** — Export and share analysis reports

### Scoring Engine
- **IPO Trade Score (0-100)** — Short-horizon speculation/momentum
- **Buffett Investment Score (0-100)** — Long-horizon quality and fundamentals
- **7-Factor Analysis** — Profitability, scale, valuation, history, management, capital structure, market conditions
- **Risk Identification** — Flags key contradictions and concerns

### Data Persistence
- All analyses saved to device storage
- Watchlist persists between sessions
- Offline support for previous analyses
- No data sent to cloud

## Installation

### Prerequisites
- Node.js 18+
- npm/yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS: Xcode 14+ (for iOS builds)
- Android: Android Studio + NDK (for Android builds)

### Setup

```bash
# Install dependencies
npm install

# or
yarn install
```

## Development

### Run in Expo Go (Easy)
```bash
npm start
# or
yarn start

# Then scan QR code with Expo Go app on your phone
```

### Run on iOS Simulator
```bash
npm run ios
```

### Run on Android Emulator
```bash
npm run android
```

### Run on Web (Browser)
```bash
npm run web
```

## Building for App Store

### Prerequisites
- Create Expo account: https://expo.dev/signup
- Configure EAS (Expo Application Services)

### Setup EAS
```bash
npm install -g eas-cli
eas login
eas build:configure
```

### Build for iOS
```bash
eas build --platform ios
```

### Build for Android
```bash
eas build --platform android
```

### Submit to App Store
```bash
# iOS
eas submit --platform ios

# Android
eas submit --platform android
```

## Project Structure

```
axiom-ipo-intelligence/
├── App.tsx                 # Main app component & navigation
├── app.json               # Expo config
├── package.json           # Dependencies
├── src/
│   ├── context/
│   │   └── AnalysisContext.tsx   # Global state management
│   ├── screens/
│   │   ├── AnalyzeScreen.tsx     # IPO input & scoring
│   │   ├── BacktestScreen.tsx    # Historical validation
│   │   ├── DetailScreen.tsx      # Score details & sharing
│   │   ├── WatchlistScreen.tsx   # Saved IPOs
│   │   ├── HistoryScreen.tsx     # Analysis history
│   │   └── SettingsScreen.tsx    # App settings
│   └── utils/
│       ├── api.ts        # Backend API calls
│       └── storage.ts    # Local storage helpers
└── assets/               # Icons, images, fonts
```

## API Integration

The app connects to Flask backend at `http://localhost:5000`

### Endpoints Used
- `POST /api/score` — Score an IPO
- `GET /api/backtest/all` — Get all backtest results
- `GET /api/backtest/<symbol>` — Get single backtest result
- `GET /api/backtest/symbols` — List available historical IPOs

### Development Backend
```bash
cd axiom_ipo
python run.py
```

## Features

### Tab Navigation
1. **Analyze** — Input IPO data and get scores
2. **Backtest** — Review historical predictions
3. **Watchlist** — Track favorite IPOs
4. **History** — View past analyses
5. **Settings** — App configuration

### Analysis Features
- Save results to device
- Compare multiple analyses
- Share via email/messaging
- Export analysis summary
- Risk factor breakdown

## Customization

### Colors & Branding
Edit color scheme in screen component styles:
```typescript
const primaryColor = '#4a90e2';
const successColor = '#28a745';
const warningColor = '#ffc107';
const dangerColor = '#dc3545';
```

### API Base URL
Change backend URL in API calls (currently `http://localhost:5000`):
```typescript
const API_BASE = 'http://your-backend-url.com';
```

### Add Screens
1. Create new screen in `src/screens/ScreenName.tsx`
2. Add to navigation in `App.tsx`
3. Connect to context if needed

## Testing

### Unit Tests (To be added)
```bash
npm test
```

### E2E Tests (To be added)
```bash
npm run e2e
```

## Deployment

### iOS Deployment
1. Create Apple Developer account
2. Configure signing certificates in Xcode
3. Build with EAS: `eas build --platform ios`
4. Submit with `eas submit --platform ios`

### Android Deployment
1. Create Google Play Developer account
2. Build with EAS: `eas build --platform android`
3. Submit with `eas submit --platform android`

## Performance Optimization

- Lazy-loaded screens
- Memoized components
- AsyncStorage for persistence
- Minimal re-renders with context

## Troubleshooting

### App won't connect to backend
- Make sure Flask backend is running (`python run.py`)
- Check if URL is correct in API calls
- Verify network connectivity

### Missing dependencies
```bash
npm install
# or
expo install [package-name]
```

### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start -- --clear
```

## Future Enhancements

- User authentication & cloud sync
- Real-time IPO alerts
- More historical IPO data
- Advanced charting & visualization
- Machine learning score optimization
- Sector-specific cohort analysis
- Dark mode implementation
- Multiple language support

## Support

For issues or feature requests:
- GitHub Issues: [repo/issues]
- Email: support@axiom.enterprises
- Docs: [documentation site]

## License

Axiom Enterprises © 2026

## Disclaimer

This app is for educational research and historical analysis only. Not investment advice. Past performance doesn't guarantee future results. Always consult a financial advisor before making investment decisions.

---

**Status:** MVP Ready for App Store  
**Version:** 1.0.0  
**Last Updated:** August 2026
