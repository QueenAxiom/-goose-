import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, SafeAreaView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAnalysis } from '../context/AnalysisContext';

const HistoryScreen = () => {
  const { analyses, removeAnalysis, clearHistory } = useAnalysis();

  const handleClear = () => {
    Alert.alert(
      'Clear History',
      'Are you sure you want to delete all analysis history?',
      [
        { text: 'Cancel', onPress: () => {} },
        { text: 'Delete', onPress: clearHistory, style: 'destructive' },
      ]
    );
  };

  const renderHistoryItem = ({ item }: any) => (
    <View style={styles.item}>
      <View style={styles.itemContent}>
        <Text style={styles.itemName}>{item.company_name}</Text>
        <Text style={styles.itemDate}>{new Date(item.timestamp).toLocaleDateString()}</Text>
        <View style={styles.scores}>
          <View style={styles.scoreTag}>
            <Text style={styles.scoreTagText}>Trade: {item.ipo_trade_score}</Text>
          </View>
          <View style={styles.scoreTag}>
            <Text style={styles.scoreTagText}>Buffett: {item.buffett_score}</Text>
          </View>
        </View>
      </View>
      <TouchableOpacity onPress={() => removeAnalysis(item.id)}>
        <Ionicons name="trash" size={20} color="#dc3545" />
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {analyses.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="list-outline" size={64} color="#ccc" />
          <Text style={styles.emptyText}>No analysis history</Text>
          <Text style={styles.emptySubtext}>Your analyses will appear here</Text>
        </View>
      ) : (
        <>
          <FlatList
            data={analyses}
            renderItem={renderHistoryItem}
            keyExtractor={(item) => item.id}
            style={styles.list}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
          />
          <TouchableOpacity style={styles.clearButton} onPress={handleClear}>
            <Ionicons name="trash-bin" size={18} color="#fff" />
            <Text style={styles.clearButtonText}>Clear All History</Text>
          </TouchableOpacity>
        </>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  list: {
    flex: 1,
  },
  item: {
    backgroundColor: '#fff',
    padding: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemContent: {
    flex: 1,
  },
  itemName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  itemDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  scores: {
    flexDirection: 'row',
    marginTop: 8,
    gap: 8,
  },
  scoreTag: {
    backgroundColor: '#4a90e2',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scoreTagText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  separator: {
    height: 1,
    backgroundColor: '#e0e0e0',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
    marginTop: 15,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#bbb',
    marginTop: 5,
  },
  clearButton: {
    backgroundColor: '#dc3545',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 15,
    margin: 10,
    borderRadius: 10,
    gap: 8,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default HistoryScreen;
