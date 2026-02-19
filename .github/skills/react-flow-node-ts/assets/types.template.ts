import { Node } from '@xyflow/react';

/**
 * {{NodeData}} - Data structure for {{NodeName}}
 * 
 * Extends Record<string, unknown> for React Flow compatibility.
 */
export interface {{NodeData}} extends Record<string, unknown> {
  /** Display title for the node */
  title: string;
  
  /** Optional description */
  description?: string;
  
  // Add additional properties specific to this node type
}

/**
 * {{NodeName}} type alias for React Flow
 * 
 * Usage:
 * ```typescript
 * const node: {{NodeName}} = {
 *   id: 'unique-id',
 *   type: '{{nodeType}}',
 *   position: { x: 0, y: 0 },
 *   data: { title: 'Example' },
 * };
 * ```
 */
export type {{NodeName}} = Node<{{NodeData}}, '{{nodeType}}'>;

// Remember to add {{NodeName}} to the AppNode union type in types/index.ts:
// export type AppNode = VideoNode | ImageNode | ... | {{NodeName}};
