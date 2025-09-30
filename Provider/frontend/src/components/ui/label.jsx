import React from "react";
import { cn } from "./utils";

function Label({ className, children, ...props }) {
  return (
    <label
      className={cn(
        "text-sm font-medium text-gray-700",
        className
      )}
      {...props}
    >
      {children}
    </label>
  );
}

export { Label };