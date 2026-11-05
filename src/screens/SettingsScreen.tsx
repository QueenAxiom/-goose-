import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  SafeAreaView,
  Alert,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const SettingsScreen = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);

  const handleOpenLink = (url: string) => {
    Linking.openURL(url).catch(() => Alert.alert('Error', 'Could not open link'));
  };

  const SettingItem = ({ icon, label, onPress, rightElement }: any) => (
    <TouchableOpacity style={styles.settingItem} onPress={onPress}>
      <View style={styles.settingLeft}>
        <Ionicons name={icon} size={20} color="#4a90e2" style={{ marginRight: 15 }} />
        <Text style={styles.settingLabel}>{label}</Text>
      </View>
      {rightElement || <Ionicons name="chevron-forward" size={20} color="#ccc" />}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Account Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>App Settings</Text>
          <SettingItem
            icon="moon"
            label="Dark Mode"
            rightElement={
              <Switch
                value={darkMode}
                onValueChange={setDarkMode}
                trackColor={{ false: '#ccc', true: '#4a90e2' }}
                thumbColor={darkMode ? '#fff' : '#fff'}
              />
            }
          />
          <SettingItem
            icon="notifications"
            label="Notifications"
            rightElement={
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#ccc', true: '#4a90e2' }}
                thumbColor={notifications ? '#fff' : '#fff'}
              />
            }
          />
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <SettingItem
            icon="information-circle"
            label="App Version"
            onPress={() => Alert.alert('Version', 'Axiom IPO Intelligence v1.0.0')}
          />
          <SettingItem
            icon="globe"
            label="Visit Website"
            onPress={() => handleOpenLink('https://axiom.enterprises')}
          />
          <SettingItem
            icon="mail"
            label="Contact Support"
            onPress={() => handleOpenLink('mailto:support@axiom.enterprises')}
          />
        </View>

        {/* Legal Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Legal</Text>
          <SettingItem
            icon="document-text"
            label="Terms of Service"
            onPress={() => handleOpenLink('https://axiom.enterprises/terms')}
          />
          <SettingItem
            icon="shield-checkmark"
            label="Privacy Policy"
            onPress={() => handleOpenLink('https://axiom.enterprises/privacy')}
          />
          <SettingItem
            icon="warning"
            label="Disclaimer"
            onPress={() =>
              Alert.alert(
                'Disclaimer',
                'Axiom IPO Intelligence provides educational research and historical analysis only. Not investment advice.'
              )
            }
          />
        </View>

        {/* Info Box */}
        <View style={styles.infoBox}>
          <Ionicons name="bulb" size={24} color="#ffc107" style={{ marginRight: 10 }} />
          <Text style={styles.infoText}>
            Axiom IPO Intelligence evaluates IPOs using historical data and point-in-time information. Past performance does not guarantee future results.
          </Text>
        </View>

        <View style={styles.spacing} />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  section: {
    backgroundColor: '#fff',
    marginHorizontal: 10,
    marginVertical: 10,
    borderRadius: 10,
    overflow: 'hidden',
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#999',
    paddingHorizontal: 15,
    paddingTop: 15,
    paddingBottom: 10,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingLabel: {
    fontSize: 15,
    color: '#333',
    fontWeight: '500',
  },
  infoBox: {
    backgroundColor: '#fffbf0',
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    flexDirection: 'row',
  },
  infoText: {
    flex: 1,
    fontSize: 13,
    color: '#666',
    lineHeight: 20,
  },
  spacing: {
    height: 30,
  },
});

export default SettingsScreen;
