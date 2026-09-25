import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Switch,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAnalysis } from '../context/AnalysisContext';

const { width } = Dimensions.get('window');

const AnalyzeScreen = ({ navigation }: any) => {
  const { addAnalysis } = useAnalysis();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    company_name: '',
    ipo_date: new Date().toISOString().split('T')[0],
    annual_revenue: '',
    price_to_sales: '',
    company_age_years: '',
    market_conditions: 'warm',
    expected_volatility: 'medium',
    public_float_pct: '20',
    profitable: false,
    management_berkshire_history: false,
  });

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData({ ...formData, [field]: value });
  };

  const scoreIPO = async () => {
    if (!formData.company_name.trim()) {
      Alert.alert('Required', 'Please enter company name');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: formData.company_name,
          ipo_date: formData.ipo_date,
          profitable: formData.profitable,
          annual_revenue: parseFloat(formData.annual_revenue || '0'),
          price_to_sales: parseFloat(formData.price_to_sales || '1'),
          company_age_years: parseInt(formData.company_age_years || '0'),
          management_berkshire_history: formData.management_berkshire_history,
          market_conditions: formData.market_conditions,
          expected_volatility: formData.expected_volatility,
          public_float_pct: parseFloat(formData.public_float_pct || '20'),
        }),
      });

      const result = await response.json();

      if (result.success) {
        addAnalysis({
          company_name: result.company_name,
          ipo_date: result.ipo_date,
          ipo_trade_score: result.ipo_trade_score,
          buffett_score: result.buffett_score,
          summary: result.summary,
        });

        navigation.navigate('Detail', { analysis: result });
      } else {
        Alert.alert('Error', result.error || 'Failed to analyze IPO');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to connect to server. Make sure Flask app is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Analyze an IPO</Text>
        <Text style={styles.headerSubtitle}>Enter company details to get scores</Text>
      </View>

      {/* Company Name */}
      <View style={styles.section}>
        <Text style={styles.label}>Company Name</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., TechCorp Inc."
          value={formData.company_name}
          onChangeText={(value) => handleInputChange('company_name', value)}
          placeholderTextColor="#999"
        />
      </View>

      {/* IPO Date */}
      <View style={styles.section}>
        <Text style={styles.label}>IPO Date</Text>
        <TextInput
          style={styles.input}
          placeholder="YYYY-MM-DD"
          value={formData.ipo_date}
          onChangeText={(value) => handleInputChange('ipo_date', value)}
          placeholderTextColor="#999"
        />
      </View>

      {/* Financial Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Financial Metrics</Text>

        <Text style={styles.label}>Annual Revenue ($M)</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., 250"
          value={formData.annual_revenue}
          onChangeText={(value) => handleInputChange('annual_revenue', value)}
          keyboardType="decimal-pad"
          placeholderTextColor="#999"
        />

        <Text style={styles.label}>Price-to-Sales Ratio</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., 5.0"
          value={formData.price_to_sales}
          onChangeText={(value) => handleInputChange('price_to_sales', value)}
          keyboardType="decimal-pad"
          placeholderTextColor="#999"
        />

        <Text style={styles.label}>Company Age (years)</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., 5"
          value={formData.company_age_years}
          onChangeText={(value) => handleInputChange('company_age_years', value)}
          keyboardType="number-pad"
          placeholderTextColor="#999"
        />

        <Text style={styles.label}>Public Float (%)</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., 20"
          value={formData.public_float_pct}
          onChangeText={(value) => handleInputChange('public_float_pct', value)}
          keyboardType="decimal-pad"
          placeholderTextColor="#999"
        />
      </View>

      {/* Conditions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Market Conditions</Text>

        <Text style={styles.label}>Market Conditions</Text>
        <View style={styles.segmentedControl}>
          {['cold', 'warm', 'hot'].map((condition) => (
            <TouchableOpacity
              key={condition}
              style={[
                styles.segment,
                formData.market_conditions === condition && styles.segmentActive,
              ]}
              onPress={() => handleInputChange('market_conditions', condition)}
            >
              <Text
                style={[
                  styles.segmentText,
                  formData.market_conditions === condition && styles.segmentTextActive,
                ]}
              >
                {condition.charAt(0).toUpperCase() + condition.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Expected Volatility</Text>
        <View style={styles.segmentedControl}>
          {['low', 'medium', 'high'].map((vol) => (
            <TouchableOpacity
              key={vol}
              style={[
                styles.segment,
                formData.expected_volatility === vol && styles.segmentActive,
              ]}
              onPress={() => handleInputChange('expected_volatility', vol)}
            >
              <Text
                style={[
                  styles.segmentText,
                  formData.expected_volatility === vol && styles.segmentTextActive,
                ]}
              >
                {vol.charAt(0).toUpperCase() + vol.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Flags */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Characteristics</Text>

        <View style={styles.toggleRow}>
          <Text style={styles.toggleLabel}>Profitable at IPO</Text>
          <Switch
            value={formData.profitable}
            onValueChange={(value) => handleInputChange('profitable', value)}
            trackColor={{ false: '#ccc', true: '#4a90e2' }}
            thumbColor={formData.profitable ? '#fff' : '#fff'}
          />
        </View>

        <View style={styles.toggleRow}>
          <Text style={styles.toggleLabel}>Management backed by Berkshire</Text>
          <Switch
            value={formData.management_berkshire_history}
            onValueChange={(value) => handleInputChange('management_berkshire_history', value)}
            trackColor={{ false: '#ccc', true: '#4a90e2' }}
            thumbColor={formData.management_berkshire_history ? '#fff' : '#fff'}
          />
        </View>
      </View>

      {/* Submit Button */}
      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={scoreIPO}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <>
            <Ionicons name="bar-chart" size={20} color="#fff" style={{ marginRight: 8 }} />
            <Text style={styles.buttonText}>Analyze IPO</Text>
          </>
        )}
      </TouchableOpacity>

      <View style={styles.spacing} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
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
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#e8f0ff',
  },
  section: {
    padding: 15,
    backgroundColor: '#fff',
    marginTop: 10,
    marginHorizontal: 10,
    borderRadius: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 14,
    backgroundColor: '#f9f9f9',
  },
  segmentedControl: {
    flexDirection: 'row',
    marginBottom: 15,
    borderRadius: 8,
    overflow: 'hidden',
  },
  segment: {
    flex: 1,
    paddingVertical: 10,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#e0e0e0',
  },
  segmentActive: {
    backgroundColor: '#4a90e2',
  },
  segmentText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  segmentTextActive: {
    color: '#fff',
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  toggleLabel: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  button: {
    backgroundColor: '#4a90e2',
    paddingVertical: 15,
    marginHorizontal: 10,
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  spacing: {
    height: 30,
  },
});

export default AnalyzeScreen;
