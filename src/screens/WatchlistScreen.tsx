import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAnalysis } from '../context/AnalysisContext';

const WatchlistScreen = () => {
  const { watchlist, removeFromWatchlist } = useAnalysis();

  const renderWatchlistItem = ({ item }: any) => (
    <View style={styles.item}>
      <View style={styles.itemContent}>
        <Text style={styles.itemName}>{item.company_name}</Text>
        <Text style={styles.itemDate}>{item.ipo_date}</Text>
        <View style={styles.scores}>
          <View style={styles.scoreTag}>
            <Text style={styles.scoreTagText}>{item.buffett_score}/100</Text>
          </View>
          <Text style={styles.scoreLabel}>Buffett Score</Text>
        </View>
      </View>
      <TouchableOpacity onPress={() => removeFromWatchlist(item.id)}>
        <Ionicons name="close-circle" size={24} color="#dc3545" />
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {watchlist.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="bookmark-outline" size={64} color="#ccc" />
          <Text style={styles.emptyText}>No IPOs in watchlist</Text>
          <Text style={styles.emptySubtext}>Add IPOs from analysis results</Text>
        </View>
      ) : (
        <FlatList
          data={watchlist}
          renderItem={renderWatchlistItem}
          keyExtractor={(item) => item.id}
          style={styles.list}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
        />
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
    alignItems: 'center',
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
    fontSize: 12,
    fontWeight: '600',
  },
  scoreLabel: {
    fontSize: 12,
    color: '#666',
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
});

export default WatchlistScreen;
