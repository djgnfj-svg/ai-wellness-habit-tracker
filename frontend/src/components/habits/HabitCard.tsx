import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZES, SPACING } from '../../constants';

interface HabitCardProps {
  id: string;
  name: string;
  emoji: string;
  target: number;
  completed: number;
  isCompleted: boolean;
  scheduledTime?: string;
  onToggle: (id: string) => void;
  style?: ViewStyle;
}

export const HabitCard: React.FC<HabitCardProps> = ({
  id,
  name,
  emoji,
  target,
  completed,
  isCompleted,
  scheduledTime,
  onToggle,
  style,
}) => {
  const completionRate = target > 0 ? (completed / target) * 100 : 0;

  return (
    <TouchableOpacity
      style={[
        styles.container,
        isCompleted && styles.completedContainer,
        style,
      ]}
      onPress={() => onToggle(id)}
      activeOpacity={0.7}
    >
      <View style={styles.content}>
        <View style={styles.habitInfo}>
          <Text style={styles.emoji}>{emoji}</Text>
          <View style={styles.textContainer}>
            <Text
              style={[
                styles.habitName,
                isCompleted && styles.completedText,
              ]}
            >
              {name}
            </Text>
            {target > 1 && (
              <Text style={styles.progress}>
                ({completed}/{target})
              </Text>
            )}
            {scheduledTime && !isCompleted && (
              <Text style={styles.scheduledTime}>
                ⏰ {scheduledTime}
              </Text>
            )}
            {target > 1 && (
              <View style={styles.progressBarContainer}>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressBarFill,
                      { width: `${Math.min(completionRate, 100)}%` },
                      isCompleted && styles.completedProgressBar,
                    ]}
                  />
                </View>
                <Text style={styles.progressPercentage}>
                  {Math.round(completionRate)}%
                </Text>
              </View>
            )}
          </View>
        </View>
        
        <View style={[
          styles.statusContainer,
          isCompleted ? styles.completedStatus : styles.pendingStatus,
        ]}>
          {isCompleted ? (
            <Ionicons name="checkmark" size={16} color="white" />
          ) : (
            <View style={styles.pendingCircle} />
          )}
        </View>
      </View>

      {/* Streak indicator for completed habits */}
      {isCompleted && (
        <View style={styles.streakIndicator}>
          <Text style={styles.streakText}>🔥 완료!</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.BACKGROUND.SECONDARY,
    borderRadius: 12,
    padding: SPACING.LG,
    marginBottom: SPACING.MD,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  completedContainer: {
    backgroundColor: '#F0FDF4',
    borderWidth: 1,
    borderColor: COLORS.SUCCESS + '30',
  },
  content: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  habitInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  emoji: {
    fontSize: 24,
    marginRight: SPACING.MD,
  },
  textContainer: {
    flex: 1,
  },
  habitName: {
    fontSize: FONT_SIZES.BODY,
    fontWeight: '600',
    color: COLORS.TEXT.PRIMARY,
    marginBottom: 2,
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: COLORS.TEXT.SECONDARY,
  },
  progress: {
    fontSize: FONT_SIZES.CAPTION,
    color: COLORS.TEXT.SECONDARY,
    marginBottom: 4,
  },
  scheduledTime: {
    fontSize: FONT_SIZES.CAPTION,
    color: COLORS.SECONDARY,
    marginBottom: 4,
  },
  progressBarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.SM,
    marginTop: 4,
  },
  progressBar: {
    flex: 1,
    height: 4,
    backgroundColor: COLORS.BORDER.PRIMARY,
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: COLORS.PRIMARY,
    borderRadius: 2,
  },
  completedProgressBar: {
    backgroundColor: COLORS.SUCCESS,
  },
  progressPercentage: {
    fontSize: FONT_SIZES.CAPTION,
    color: COLORS.TEXT.SECONDARY,
    fontWeight: '500',
    minWidth: 35,
    textAlign: 'right',
  },
  statusContainer: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  completedStatus: {
    backgroundColor: COLORS.SUCCESS,
  },
  pendingStatus: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: COLORS.BORDER.SECONDARY,
  },
  pendingCircle: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.BORDER.SECONDARY,
  },
  streakIndicator: {
    marginTop: SPACING.SM,
    alignSelf: 'flex-start',
  },
  streakText: {
    fontSize: FONT_SIZES.CAPTION,
    color: COLORS.SUCCESS,
    fontWeight: '600',
  },
});