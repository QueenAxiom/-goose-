import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const EducationDetailScreen = ({ route, navigation }: any) => {
  const { module: moduleName } = route.params || {};
  const [module, setModule] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModule();
  }, []);

  const loadModule = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/education/${moduleName}`);
      const data = await response.json();

      if (data.success) {
        setModule(data.module);
      } else {
        Alert.alert('Error', 'Failed to load module');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4a90e2" />
          <Text style={styles.loadingText}>Loading module...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!module) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.error}>Module not found</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>{module.title}</Text>
        </View>

        {module.sections && module.sections.map((section: any, index: number) => (
          <View key={index} style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="bookmark" size={20} color="#4a90e2" style={{ marginRight: 10 }} />
              <Text style={styles.sectionTitle}>{section.title}</Text>
            </View>
            <Text style={styles.sectionContent}>{section.content}</Text>
          </View>
        ))}

        {/* Key Takeaways */}
        <View style={styles.takeawaysSection}>
          <Text style={styles.takeawaysTitle}>🎯 Key Takeaways</Text>
          <View style={styles.takeawayItem}>
            <Ionicons name="checkmark-circle" size={16} color="#28a745" style={{ marginRight: 10 }} />
            <Text style={styles.takeawayText}>Understand the concepts</Text>
          </View>
          <View style={styles.takeawayItem}>
            <Ionicons name="checkmark-circle" size={16} color="#28a745" style={{ marginRight: 10 }} />
            <Text style={styles.takeawayText}>Apply to your IPO analysis</Text>
          </View>
          <View style={styles.takeawayItem}>
            <Ionicons name="checkmark-circle" size={16} color="#28a745" style={{ marginRight: 10 }} />
            <Text style={styles.takeawayText}>Risk management first</Text>
          </View>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#999',
  },
  header: {
    backgroundColor: '#4a90e2',
    padding: 20,
    paddingTop: 30,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  section: {
    backgroundColor: '#fff',
    marginHorizontal: 10,
    marginVertical: 10,
    padding: 15,
    borderRadius: 10,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  sectionContent: {
    fontSize: 14,
    color: '#555',
    lineHeight: 22,
  },
  takeawaysSection: {
    backgroundColor: '#fff',
    marginHorizontal: 10,
    marginVertical: 10,
    padding: 15,
    borderRadius: 10,
  },
  takeawaysTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  takeawayItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  takeawayText: {
    fontSize: 13,
    color: '#555',
  },
  error: {
    textAlign: 'center',
    padding: 20,
    color: '#dc3545',
    fontSize: 16,
  },
  spacing: {
    height: 30,
  },
});

export default EducationDetailScreen;
