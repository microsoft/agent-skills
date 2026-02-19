import { memo, useCallback } from 'react';
import { NodeProps, Node, Handle, Position, NodeResizer } from '@xyflow/react';
import { {{NodeData}} } from '@/types';
import { useAppStore } from '@/store';
import { cn } from '@/utils/utils';

type {{NodeName}}Props = NodeProps<Node<{{NodeData}}>>;

/**
 * {{NodeName}} - Description of what this node does
 * 
 * @example
 * // Node data structure
 * const data: {{NodeData}} = {
 *   title: 'Example',
 *   // ... other properties
 * };
 */
export const {{NodeName}} = memo(function {{NodeName}}({
  id,
  data,
  selected,
  width,
  height,
}: {{NodeName}}Props) {
  // Store selectors - use individual selectors for performance
  const updateNode = useAppStore((state) => state.updateNode);
  const canvasMode = useAppStore((state) => state.canvasMode);
  const isEditing = canvasMode === 'editing';

  // Handlers
  const handleTitleChange = useCallback(
    (title: string) => {
      updateNode(id, { title });
    },
    [id, updateNode]
  );

  return (
    <>
      {/* NodeResizer - only visible in editing mode */}
      {isEditing && (
        <NodeResizer
          minWidth={200}
          minHeight={150}
          isVisible={selected}
          lineClassName="!border-[var(--frontier-primary)]"
          handleClassName="!w-2 !h-2 !bg-[var(--frontier-primary)] !border-none"
        />
      )}

      {/* Node Container */}
      <div
        className={cn(
          'bg-[var(--frontier-surface)]',
          'border-2 rounded-xl overflow-hidden',
          'transition-all duration-200',
          selected
            ? 'border-[var(--frontier-primary)] shadow-lg shadow-[var(--frontier-primary)]/20'
            : 'border-[var(--frontier-border)]'
        )}
        style={{ width: width ?? 280, height: height ?? 'auto' }}
      >
        {/* Target Handle (top) */}
        <Handle
          type="target"
          position={Position.Top}
          className="!w-3 !h-3 !bg-[var(--frontier-primary)] !border-2 !border-[var(--frontier-surface)]"
        />

        {/* Node Header */}
        <div className="px-4 py-3 border-b border-[var(--frontier-border)]">
          {isEditing ? (
            <input
              type="text"
              value={data.title}
              onChange={(e) => handleTitleChange(e.target.value)}
              className={cn(
                'w-full bg-transparent text-[var(--frontier-text)]',
                'font-semibold text-sm outline-none',
                'focus:ring-1 focus:ring-[var(--frontier-primary)] rounded px-1'
              )}
            />
          ) : (
            <h3 className="text-[var(--frontier-text)] font-semibold text-sm truncate">
              {data.title}
            </h3>
          )}
        </div>

        {/* Node Content */}
        <div className="p-4">
          {/* Add node-specific content here */}
          <p className="text-[var(--frontier-text-muted)] text-xs">
            Node content goes here
          </p>
        </div>

        {/* Source Handle (bottom) */}
        <Handle
          type="source"
          position={Position.Bottom}
          className="!w-3 !h-3 !bg-[var(--frontier-primary)] !border-2 !border-[var(--frontier-surface)]"
        />
      </div>
    </>
  );
});
