import { z } from 'zod';

export const chatMessageSchema = z.object({
  content: z.string().min(1, 'Message cannot be empty').max(4000, 'Message too long'),
  session_id: z.string().optional(),
  context: z.record(z.any()).optional(),
});

export const validateMessage = (message: string, maxLength: number = 4000): string | null => {
  if (!message.trim()) {
    return 'Message cannot be empty';
  }
  
  if (message.length > maxLength) {
    return `Message too long (max ${maxLength} characters)`;
  }
  
  return null;
};

export type ChatMessageInput = z.infer<typeof chatMessageSchema>;