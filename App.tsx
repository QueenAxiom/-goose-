import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import * as AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { View, Text, SafeAreaView } from 'react-native';

// Screens
import AnalyzeScreen from './src/screens/AnalyzeScreen';
import BacktestScreen from './src/screens/BacktestScreen';
import WatchlistScreen from './src/screens/WatchlistScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import DetailScreen from './src/screens/DetailScreen';

// Context for shared state
import { AnalysisProvider } from './src/context/AnalysisContext';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const AnalyzeStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: {
        backgroundColor: '#4a90e2',
      },
      headerTintColor: '#fff',
      headerTitleStyle: {
        fontWeight: 'bold',
      },
    }}
  >
    <Stack.Screen
      name="AnalyzeHome"
      component={AnalyzeScreen}
      options={{ title: 'Analyze IPO' }}
    />
    <Stack.Screen
      name="Detail"
      component={DetailScreen}
      options={{ title: 'IPO Analysis Result' }}
    />
  </Stack.Navigator>
);

const BacktestStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerStyle: {
        backgroundColor: '#4a90e2',
      },
      headerTintColor: '#fff',
      headerTitleStyle: {
        fontWeight: 'bold',
      },
    }}
  >
    <Stack.Screen
      name="BacktestHome"
      component={BacktestScreen}
      options={{ title: 'Historical Backtest' }}
    />
    <Stack.Screen
      name="BacktestDetail"
      component={DetailScreen}
      options={{ title: 'Historical IPO Analysis' }}
    />
  </Stack.Navigator>
);

export default function App() {
  return (
    <AnalysisProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            headerShown: false,
            tabBarIcon: ({ focused, color, size }) => {
              let iconName;

              if (route.name === 'Analyze') {
                iconName = focused ? 'bar-chart' : 'bar-chart-outline';
              } else if (route.name === 'Backtest') {
                iconName = focused ? 'time' : 'time-outline';
              } else if (route.name === 'Watchlist') {
                iconName = focused ? 'bookmark' : 'bookmark-outline';
              } else if (route.name === 'History') {
                iconName = focused ? 'list' : 'list-outline';
              } else if (route.name === 'Settings') {
                iconName = focused ? 'settings' : 'settings-outline';
              }

              return <Ionicons name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#4a90e2',
            tabBarInactiveTintColor: '#999',
            tabBarStyle: {
              borderTopColor: '#e0e0e0',
              borderTopWidth: 1,
            },
          })}
        >
          <Tab.Screen
            name="Analyze"
            component={AnalyzeStack}
            options={{
              title: 'Analyze',
              tabBarLabel: 'Analyze',
            }}
          />
          <Tab.Screen
            name="Backtest"
            component={BacktestStack}
            options={{
              title: 'Backtest',
              tabBarLabel: 'Backtest',
            }}
          />
          <Tab.Screen
            name="Watchlist"
            component={WatchlistScreen}
            options={{
              title: 'Watchlist',
              headerShown: true,
              headerStyle: {
                backgroundColor: '#4a90e2',
              },
              headerTintColor: '#fff',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            }}
          />
          <Tab.Screen
            name="History"
            component={HistoryScreen}
            options={{
              title: 'History',
              headerShown: true,
              headerStyle: {
                backgroundColor: '#4a90e2',
              },
              headerTintColor: '#fff',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            }}
          />
          <Tab.Screen
            name="Settings"
            component={SettingsScreen}
            options={{
              title: 'Settings',
              headerShown: true,
              headerStyle: {
                backgroundColor: '#4a90e2',
              },
              headerTintColor: '#fff',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </AnalysisProvider>
  );
}
