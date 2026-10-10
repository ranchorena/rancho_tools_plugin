export function shouldActivateRow(key, isRepeat, targetIsRow) {
	return (key === 'Enter' || key === ' ') && !isRepeat && targetIsRow;
}
