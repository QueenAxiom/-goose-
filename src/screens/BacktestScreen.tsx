import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const BacktestScreen = ({ navigation }: any) => {
  const [backtests, setBacktests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  const loadBacktest = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/backtest/all');
      const data = await response.json();
      if (data.success) {
        setBacktests(data.results);
        setMetrics({
          accuracy: data.accuracy_pct,
          total: data.total_backtests,
          correct: data.correct_predictions,
          correlation: data.correlation_buffett_vs_return,
        });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load backtest data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBacktest();
  }, []);

  const renderMetricBox = (label: string, value: string, color: string) => (
    <View style={[styles.metricBox, { backgroundColor: color }]}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );

  const renderBacktestItem = ({ item }: any) => (
    <View style={styles.resultItem}>
      <View style={styles.resultHeader}>
        <View>
          <Text style={styles.resultSymbol}>{item.symbol}</Text>
          <Text style={styles.resultCompany}>{item.company_name}</Text>
        </View>
        <View style={[styles.correctBadge, !item.correct_prediction && { backgroundColor: '#f8d7da' }]}>
          <Text style={[styles.correctText, !item.correct_prediction && { color: '#721c24' }]}>
            {item.correct_prediction ? '✓' : '✗'}
          </Text>
        </View>
      </View>
      <View style={styles.resultMetrics}>
        <View style={styles.resultMetric}>
          <Text style={styles.metricSmallLabel}>Buffett Score</Text>
          <Text style={styles.metricSmallValue}>{item.predicted_buffett_score}</Text>
        </View>
        <View style={styles.resultMetric}>
          <Text style={styles.metricSmallLabel}>3-Yr Return</Text>
          <Text style={[styles.metricSmallValue, { color: item.actual_3yr_return >= 0 ? '#28a745' : '#dc3545' }]}>
            {item.actual_3yr_return.toFixed(1)}%
          </Text>
        </View>
        <View style={styles.resultMetric}>
          <Text style={styles.metricSmallLabel}>Day 1 Return</Text>
          <Text style={styles.metricSmallValue}>{item.first_day_return.toFixed(1)}%</Text>
        </View>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Historical Backtest</Text>
        <Text style={styles.headerSubtitle}>Axiom's track record against real IPOs</Text>
      </View>

      {/* Metrics */}
      {metrics && (
        <View style={styles.metricsContainer}>
          {renderMetricBox('Accuracy', `${metrics.accuracy.toFixed(1)}%`, '#4a90e2')}
          {renderMetricBox('Tested', `${metrics.total}`, '#667eea')}
          {renderMetricBox('Correct', `${metrics.correct}`, '#28a745')}
          {renderMetricBox('Correlation', metrics.correlation.toFixed(3), '#f093fb')}
        </View>
      )}

      {/* Results List */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Backtest Results</Text>
          <TouchableOpacity onPress={loadBacktest}>
            <Ionicons name="refresh" size={20} color="#4a90e2" />
          </TouchableOpacity>
        </View>

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#4a90e2" />
            <Text style={styles.loadingText}>Loading backtest data...</Text>
          </View>
        ) : (
          <FlatList
            data={backtests}
            renderItem={renderBacktestItem}
            keyExtractor={(item) => item.symbol}
            scrollEnabled={false}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
          />
        )}
      </View>

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
  metricsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
    gap: 10,
  },
  metricBox: {
    flex: 0.48,
    borderRadius: 10,
    padding: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.9,
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  section: {
    backgroundColor: '#fff',
    marginHorizontal: 10,
    marginVertical: 10,
    borderRadius: 10,
    padding: 15,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  resultItem: {
    paddingVertical: 12,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  resultSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  resultCompany: {
    fontSize: 12,
    color: '#999',
    marginTop: 3,
  },
  correctBadge: {
    backgroundColor: '#d4edda',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  correctText: {
    color: '#155724',
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultMetrics: {
    flexDirection: 'row',
    gap: 15,
  },
  resultMetric: {
    flex: 1,
    backgroundColor: '#f9f9f9',
    padding: 10,
    borderRadius: 6,
  },
  metricSmallLabel: {
    fontSize: 11,
    color: '#999',
    marginBottom: 3,
  },
  metricSmallValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  separator: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 8,
  },
  loadingContainer: {
    paddingVertical: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#999',
  },
  spacing: {
    height: 30,
  },
});

export default BacktestScreen;
