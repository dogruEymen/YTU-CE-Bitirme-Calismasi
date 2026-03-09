export type MessageCardProps = {
	id: string,
	text: string,
	sender: 'user' | 'agent',
	timestamp?: Date,
}
