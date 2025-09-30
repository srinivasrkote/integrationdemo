import React, { useState, useContext, createContext } from 'react';
import { cn } from './utils';

const DialogContext = createContext();

export function Dialog({ open, onOpenChange, children }) {
  return (
    <DialogContext.Provider value={{ open, onOpenChange }}>
      {children}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div 
            className="fixed inset-0 bg-black/50" 
            onClick={() => onOpenChange?.(false)}
          />
          <div className="relative z-50 max-h-[90vh] overflow-auto">
            {children}
          </div>
        </div>
      )}
    </DialogContext.Provider>
  );
}

export function DialogTrigger({ asChild, children, ...props }) {
  const { onOpenChange } = useContext(DialogContext);
  
  const handleClick = () => {
    onOpenChange?.(true);
  };

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      onClick: handleClick,
      ...props
    });
  }

  return (
    <button onClick={handleClick} {...props}>
      {children}
    </button>
  );
}

export function DialogContent({ className, children, ...props }) {
  const { open, onOpenChange } = useContext(DialogContext);
  
  if (!open) return null;

  return (
    <div 
      className={cn(
        "bg-white rounded-lg shadow-lg p-6 w-full max-w-md mx-4",
        className
      )}
      onClick={(e) => e.stopPropagation()}
      {...props}
    >
      {children}
    </div>
  );
}

export function DialogHeader({ className, children, ...props }) {
  return (
    <div 
      className={cn("space-y-2 mb-4", className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function DialogTitle({ className, children, ...props }) {
  return (
    <h2 
      className={cn("text-lg font-semibold text-gray-900", className)}
      {...props}
    >
      {children}
    </h2>
  );
}

export function DialogDescription({ className, children, ...props }) {
  return (
    <p 
      className={cn("text-sm text-gray-600", className)}
      {...props}
    >
      {children}
    </p>
  );
}