import React from "react";
import { cn } from "./utils";

function Table({ className, children, ...props }) {
  return (
    <div className="relative w-full overflow-auto">
      <table
        className={cn("w-full caption-bottom text-sm", className)}
        {...props}
      >
        {children}
      </table>
    </div>
  );
}

function TableHeader({ className, children, ...props }) {
  return (
    <thead className={cn("[&_tr]:border-b", className)} {...props}>
      {children}
    </thead>
  );
}

function TableBody({ className, children, ...props }) {
  return (
    <tbody
      className={cn("[&_tr:last-child]:border-0", className)}
      {...props}
    >
      {children}
    </tbody>
  );
}

function TableRow({ className, children, ...props }) {
  return (
    <tr
      className={cn(
        "border-b transition-colors hover:bg-gray-50 data-[state=selected]:bg-gray-100",
        className
      )}
      {...props}
    >
      {children}
    </tr>
  );
}

function TableHead({ className, children, ...props }) {
  return (
    <th
      className={cn(
        "h-12 px-4 text-left align-middle font-medium text-gray-500 [&:has([role=checkbox])]:pr-0",
        className
      )}
      {...props}
    >
      {children}
    </th>
  );
}

function TableCell({ className, children, ...props }) {
  return (
    <td
      className={cn("p-4 align-middle [&:has([role=checkbox])]:pr-0", className)}
      {...props}
    >
      {children}
    </td>
  );
}

export {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
};