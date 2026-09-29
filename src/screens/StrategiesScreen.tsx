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
  SafeAreaView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const StrategiesScreen = ({ route, navigation }: any) => {
  const { ipo_trade_score, buffett_score, market_conditions } = route.params || {};
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [showEducation, setShowEducation] = useState(false);
  const [educationModules, setEducationModules] = useState([]);

  useEffect(() => {
    if (ipo_trade_score !== undefined) {
      loadStrategies();
    }
    loadEducation();
  }, []);

  const loadStrategies = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/strategies/recommended', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ipo_trade_score: ipo_trade_score || 50,
          buffett_score: buffett_score || 50,
          market_conditions: market_conditions || 'warm',
        }),
      });

      const data = await response.json();
      if (data.success) {
        setStrategies(data.recommendations);
      }
    } catch (error) {
      console.error('Error loading strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadEducation = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/education/modules');
      const data = await response.json();
      if (data.success) {
        setEducationModules(data.modules);
      }
    } catch (error) {
      console.error('Error loading education:', error);
    }
  };

  const getSuitabilityColor = (suitability: string) => {
    switch (suitability) {
      case 'HIGH':
        return '#28a745';
      case 'MEDIUM-HIGH':
        return '#ffc107';
      case 'MEDIUM':
        return '#ff9800';
      default:
        return '#dc3545';
    }
  };

  const renderStrategyItem = ({ item }: any) => (
    <TouchableOpacity
      style={[styles.strategyCard, { borderLeftColor: getSuitabilityColor(item.suitability) }]}
      onPress={() => setSelectedStrategy(item)}
    >
      <View style={styles.strategyHeader}>
        <Text style={styles.strategyName}>{item.strategy}</Text>
        <View style={[styles.suitabilityBadge, { backgroundColor: getSuitabilityColor(item.suitability) }]}>
          <Text style={styles.suitabilityText}>{item.suitability}</Text>
        </View>
      </View>
      <Text style={styles.strategyReason}>{item.reason}</Text>
      <View style={styles.strategyMeta}>
        <Text style={styles.metaItem}>📊 {item.type.replace('_', ' ')}</Text>
        <Text style={styles.metaItem}>⚡ {item.risk_level}</Text>
      </View>
    </TouchableOpacity>
  );

  const renderEducationItem = ({ item }: any) => (
    <TouchableOpacity
      style={styles.eduCard}
      onPress={() => navigation.navigate('EducationDetail', { module: item })}
    >
      <Ionicons name="book" size={24} color="#4a90e2" style={{ marginBottom: 10 }} />
      <Text style={styles.eduTitle}>{item.replace('_', ' ').toUpperCase()}</Text>
      <Ionicons name="chevron-forward" size={16} color="#999" />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Recommended Strategies Section */}
        {ipo_trade_score !== undefined && (
          <>
            <View style={styles.header}>
              <Text style={styles.headerTitle}>Recommended Strategies</Text>
              <Text style={styles.headerSubtitle}>
                Based on your scores: Trade {ipo_trade_score} / Buffett {buffett_score}
              </Text>
            </View>

            {loading ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#4a90e2" />
                <Text style={styles.loadingText}>Loading strategies...</Text>
              </View>
            ) : strategies.length > 0 ? (
              <FlatList
                data={strategies}
                renderItem={renderStrategyItem}
                keyExtractor={(item, index) => index.toString()}
                scrollEnabled={false}
                style={styles.strategiesList}
              />
            ) : (
              <Text style={styles.noStrategies}>No strategies match your profile</Text>
            )}
          </>
        )}

        {/* Education Section */}
        <View style={styles.educationSection}>
          <Text style={styles.sectionTitle}>Trading Education</Text>
          <Text style={styles.sectionSubtitle}>Learn IPO trading & risk management</Text>

          <FlatList
            data={educationModules}
            renderItem={renderEducationItem}
            keyExtractor={(item) => item}
            scrollEnabled={false}
            numColumns={2}
            columnWrapperStyle={styles.educationGrid}
          />
        </View>

        {/* Daily Trading Tips */}
        <View style={styles.tipsSection}>
          <Text style={styles.tipsTitle}>💡 Daily Trading Tip</Text>
          <Text style={styles.tipsContent}>
            IPO hype peaks on day 1. Best long-term gains often come 1-2 weeks later when excitement fades and quality becomes apparent.
          </Text>
          <TouchableOpacity style={styles.tipsButton} onPress={loadEducation}>
            <Text style={styles.tipsButtonText}>Get Another Tip</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Strategy Detail Modal */}
      {selectedStrategy && (
        <View style={styles.modal}>
          <View style={styles.modalContent}>
            <TouchableOpacity style={styles.closeButton} onPress={() => setSelectedStrategy(null)}>
              <Ionicons name="close" size={24} color="#999" />
            </TouchableOpacity>

            <Text style={styles.modalTitle}>{selectedStrategy.strategy}</Text>
            <Text style={styles.modalType}>{selectedStrategy.type.replace(/_/g, ' ').toUpperCase()}</Text>

            <View style={styles.detailSection}>
              <Text style={styles.detailLabel}>Why This Strategy?</Text>
              <Text style={styles.detailText}>{selectedStrategy.reason}</Text>
            </View>

            <View style={styles.detailSection}>
              <Text style={styles.detailLabel}>Risk & Commitment</Text>
              <View style={styles.detailRow}>
                <Text style={styles.detailKey}>Risk Level:</Text>
                <Text style={styles.detailValue}>{selectedStrategy.risk_level}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailKey}>Time Needed:</Text>
                <Text style={styles.detailValue}>{selectedStrategy.time_commitment}</Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.learnMoreButton}
              onPress={() => {
                setSelectedStrategy(null);
                Alert.alert(
                  'Strategy Guide',
                  'Visit the Trading Education section for detailed guides on this and other strategies.'
                );
              }}
            >
              <Text style={styles.learnMoreText}>Learn More in Education</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </SafeAreaView>
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
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 13,
    color: '#e8f0ff',
  },
  loadingContainer: {
    paddingVertical: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#999',
  },
  strategiesList: {
    padding: 10,
  },
  strategyCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
  },
  strategyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  strategyName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  suitabilityBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  suitabilityText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  strategyReason: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    marginBottom: 10,
  },
  strategyMeta: {
    flexDirection: 'row',
    gap: 15,
  },
  metaItem: {
    fontSize: 12,
    color: '#999',
  },
  noStrategies: {
    textAlign: 'center',
    padding: 20,
    color: '#999',
  },
  educationSection: {
    paddingHorizontal: 10,
    paddingVertical: 20,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  sectionSubtitle: {
    fontSize: 12,
    color: '#999',
    marginBottom: 15,
  },
  educationGrid: {
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  eduCard: {
    flex: 0.48,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    justifyContent: 'space-between',
    alignItems: 'center',
    minHeight: 120,
  },
  eduTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
    marginVertical: 10,
  },
  tipsSection: {
    backgroundColor: '#fff3cd',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
    marginBottom: 30,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  tipsContent: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    marginBottom: 12,
  },
  tipsButton: {
    backgroundColor: '#ffc107',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  tipsButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  modal: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    maxHeight: '80%',
  },
  closeButton: {
    alignSelf: 'flex-end',
    marginBottom: 10,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  modalType: {
    fontSize: 12,
    color: '#999',
    marginBottom: 15,
  },
  detailSection: {
    marginBottom: 15,
  },
  detailLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  detailText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
  },
  detailKey: {
    fontSize: 12,
    color: '#999',
  },
  detailValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
  },
  learnMoreButton: {
    backgroundColor: '#4a90e2',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 15,
  },
  learnMoreText: {
    color: '#fff',
    fontWeight: '600',
  },
});

export default StrategiesScreen;
