import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Share,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAnalysis } from '../context/AnalysisContext';

const DetailScreen = ({ route, navigation }: any) => {
  const { addToWatchlist } = useAnalysis();
  const data = route.params?.analysis;

  if (!data) {
    return (
      <View style={styles.container}>
        <Text>No data available</Text>
      </View>
    );
  }

  const handleShare = async () => {
    try {
      await Share.share({
        message: `${data.company_name} IPO Analysis\n\nIPO Trade Score: ${data.ipo_trade_score}/100\nBuffett Investment Score: ${data.buffett_score}/100\n\n${data.summary}`,
        title: 'Axiom IPO Analysis',
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to share');
    }
  };

  const handleAddToWatchlist = () => {
    addToWatchlist({
      id: Date.now().toString(),
      company_name: data.company_name,
      ipo_date: data.ipo_date,
      ipo_trade_score: data.ipo_trade_score,
      buffett_score: data.buffett_score,
      summary: data.summary,
      timestamp: Date.now(),
    });
    Alert.alert('Success', 'Added to watchlist');
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return '#28a745';
    if (score >= 60) return '#ffc107';
    if (score >= 40) return '#ff9800';
    return '#dc3545';
  };

  const getScoreGrade = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 65) return 'Strong';
    if (score >= 50) return 'Moderate';
    if (score >= 35) return 'Weak';
    return 'Poor';
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.companyName}>{data.company_name}</Text>
        <Text style={styles.ipoDate}>{data.ipo_date}</Text>
      </View>

      {/* Scores */}
      <View style={styles.scoresContainer}>
        <View style={styles.scoreBox}>
          <Text style={styles.scoreLabel}>IPO Trade Score</Text>
          <View style={[styles.scoreBadge, { backgroundColor: getScoreColor(data.ipo_trade_score) }]}>
            <Text style={styles.scoreNumber}>{data.ipo_trade_score}</Text>
            <Text style={styles.scoreGrade}>{getScoreGrade(data.ipo_trade_score)}</Text>
          </View>
          <Text style={styles.scoreDescription}>Short-horizon opportunity</Text>
        </View>

        <View style={styles.scoreBox}>
          <Text style={styles.scoreLabel}>Buffett Score</Text>
          <View style={[styles.scoreBadge, { backgroundColor: getScoreColor(data.buffett_score) }]}>
            <Text style={styles.scoreNumber}>{data.buffett_score}</Text>
            <Text style={styles.scoreGrade}>{getScoreGrade(data.buffett_score)}</Text>
          </View>
          <Text style={styles.scoreDescription}>Long-horizon quality</Text>
        </View>
      </View>

      {/* Summary */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Analysis Summary</Text>
        <Text style={styles.summaryText}>{data.summary}</Text>
      </View>

      {/* Factors */}
      {data.factors && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Factor Analysis</Text>
          {Object.entries(data.factors).map(([key, value]: [string, any]) => (
            <View key={key} style={styles.factorItem}>
              <Text style={styles.factorLabel}>
                {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
              </Text>
              <View style={styles.factorBar}>
                <View
                  style={[styles.factorFill, { width: `${value}%` }]}
                />
              </View>
              <Text style={styles.factorValue}>{value}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Risks */}
      {data.risks && data.risks.length > 0 && (
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: '#dc3545' }]}>Key Risks</Text>
          {data.risks.map((risk: string, index: number) => (
            <View key={index} style={styles.riskItem}>
              <Ionicons name="warning" size={16} color="#dc3545" style={{ marginRight: 10 }} />
              <Text style={styles.riskText}>{risk}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity style={styles.actionButton} onPress={handleAddToWatchlist}>
          <Ionicons name="bookmark" size={20} color="#fff" />
          <Text style={styles.actionText}>Watchlist</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton} onPress={handleShare}>
          <Ionicons name="share-social" size={20} color="#fff" />
          <Text style={styles.actionText}>Share</Text>
        </TouchableOpacity>
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
    paddingTop: 20,
  },
  companyName: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  ipoDate: {
    fontSize: 14,
    color: '#e8f0ff',
  },
  scoresContainer: {
    flexDirection: 'row',
    padding: 15,
    gap: 15,
  },
  scoreBox: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  scoreLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 10,
    fontWeight: '600',
  },
  scoreBadge: {
    borderRadius: 50,
    width: 100,
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  scoreNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
  },
  scoreGrade: {
    fontSize: 12,
    color: '#fff',
    fontWeight: '600',
    marginTop: 5,
  },
  scoreDescription: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    backgroundColor: '#fff',
    marginHorizontal: 10,
    marginVertical: 10,
    padding: 15,
    borderRadius: 10,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  summaryText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 22,
  },
  factorItem: {
    marginBottom: 12,
  },
  factorLabel: {
    fontSize: 13,
    color: '#333',
    marginBottom: 6,
    fontWeight: '500',
  },
  factorBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 6,
  },
  factorFill: {
    height: '100%',
    backgroundColor: '#4a90e2',
  },
  factorValue: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
  },
  riskItem: {
    flexDirection: 'row',
    backgroundColor: '#ffebee',
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
  },
  riskText: {
    flex: 1,
    fontSize: 12,
    color: '#d32f2f',
    lineHeight: 18,
  },
  actionsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 10,
    gap: 10,
    marginTop: 10,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#4a90e2',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 10,
    gap: 8,
  },
  actionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  spacing: {
    height: 30,
  },
});

export default DetailScreen;
